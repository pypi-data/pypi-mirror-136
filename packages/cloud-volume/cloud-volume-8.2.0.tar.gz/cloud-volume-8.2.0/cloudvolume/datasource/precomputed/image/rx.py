from functools import partial
import itertools
import math
import multiprocessing as mp
import os
import threading

import numpy as np

from cloudfiles import reset_connection_pools, CloudFiles, compression
import fastremap

from ....exceptions import EmptyVolumeException, EmptyFileException
from ....lib import (  
  mkdir, clamp, xyzrange, Vec, 
  Bbox, min2, max2, check_bounds, 
  jsonify, red, sip, first
)
from .... import chunks

from cloudvolume.scheduler import schedule_jobs
from cloudvolume.threaded_queue import DEFAULT_THREADS
from cloudvolume.volumecutout import VolumeCutout

import cloudvolume.sharedmemory as shm

from ..common import should_compress, content_type
from .common import (
  parallel_execution, 
  chunknames, shade, gridpoints,
  compressed_morton_code
)

from .. import sharding

progress_queue = None # defined in common.initialize_synchronization
fs_lock = None # defined in common.initialize_synchronization

def download_sharded(
  requested_bbox, mip,
  meta, cache, spec,
  compress, progress,
  fill_missing, 
  order, background_color
):

  full_bbox = requested_bbox.expand_to_chunk_size(
    meta.chunk_size(mip), offset=meta.voxel_offset(mip)
  )
  full_bbox = Bbox.clamp(full_bbox, meta.bounds(mip))
  shape = list(requested_bbox.size3()) + [ meta.num_channels ]
  compress_cache = should_compress(meta.encoding(mip), compress, cache, iscache=True)

  chunk_size = meta.chunk_size(mip)
  grid_size = np.ceil(meta.bounds(mip).size3() / chunk_size).astype(np.uint32)

  reader = sharding.ShardReader(meta, cache, spec)
  bounds = meta.bounds(mip)

  renderbuffer = np.zeros(shape=shape, dtype=meta.dtype, order=order)

  gpts = list(gridpoints(full_bbox, bounds, chunk_size))

  code_map = {}
  morton_codes = compressed_morton_code(gpts, grid_size)
  for gridpoint, morton_code in zip(gpts, morton_codes):
    cutout_bbox = Bbox(
      bounds.minpt + gridpoint * chunk_size,
      min2(bounds.minpt + (gridpoint + 1) * chunk_size, bounds.maxpt)
    )
    code_map[morton_code] = cutout_bbox

  single_voxel = requested_bbox.volume() == 1

  decode_fn = decode
  if single_voxel:
    decode_fn = partial(decode_single_voxel, requested_bbox.minpt - full_bbox.minpt)

  all_chunkdata = reader.get_data(list(code_map.keys()), meta.key(mip), progress=progress)
  for zcode, chunkdata in all_chunkdata.items():
    cutout_bbox = code_map[zcode]
    img3d = decode_fn(
      meta, cutout_bbox, 
      chunkdata, fill_missing, mip,
      background_color=background_color
    )
    
    if single_voxel:
      renderbuffer[:] = img3d
    else:
      shade(renderbuffer, requested_bbox, img3d, cutout_bbox)

  return VolumeCutout.from_volume(
    meta, mip, renderbuffer, 
    requested_bbox
  )

def download(
  requested_bbox, mip, 
  meta, cache,
  fill_missing, progress,
  parallel, location, 
  retain, use_shared_memory, 
  use_file, compress, order='F',
  green=False, secrets=None,
  renumber=False, background_color=0
):
  """Cutout a requested bounding box from storage and return it as a numpy array."""
  
  full_bbox = requested_bbox.expand_to_chunk_size(
    meta.chunk_size(mip), offset=meta.voxel_offset(mip)
  )
  full_bbox = Bbox.clamp(full_bbox, meta.bounds(mip))
  cloudpaths = chunknames(
    full_bbox, meta.bounds(mip), 
    meta.key(mip), meta.chunk_size(mip), 
    protocol=meta.path.protocol
  )
  shape = list(requested_bbox.size3()) + [ meta.num_channels ]

  compress_cache = should_compress(meta.encoding(mip), compress, cache, iscache=True)

  handle = None

  if renumber and (parallel != 1):
    raise ValueError("renumber is not supported for parallel operation.")

  if use_shared_memory and use_file:
    raise ValueError("use_shared_memory and use_file are mutually exclusive arguments.")

  dtype = np.uint16 if renumber else meta.dtype

  if requested_bbox.volume() == 1:
    return download_single_voxel_unsharded(
      meta, cache, 
      requested_bbox, first(cloudpaths), 
      mip, fill_missing, compress_cache,
      secrets, renumber, background_color,
    )
  elif parallel == 1:
    if use_shared_memory: # write to shared memory
      handle, renderbuffer = shm.ndarray(
        shape, dtype=dtype, order=order,
        location=location, lock=fs_lock
      )
      if not retain:
        shm.unlink(location)
    elif use_file: # write to ordinary file
      handle, renderbuffer = shm.ndarray_fs(
        shape, dtype=dtype, order=order,
        location=location, lock=fs_lock,
        emulate_shm=False
      )
      if not retain:
        os.unlink(location)
    else:
      renderbuffer = np.full(shape=shape, fill_value=background_color,
                             dtype=dtype, order=order)

    def process(img3d, bbox):
      shade(renderbuffer, requested_bbox, img3d, bbox)

    remap = { background_color: background_color }
    lock = threading.Lock()
    N = 1
    def process_renumber(img3d, bbox):
      nonlocal N
      nonlocal lock 
      nonlocal remap
      nonlocal renderbuffer
      img_labels = fastremap.unique(img3d)
      with lock:
        for lbl in img_labels:
          if lbl not in remap:
            remap[lbl] = N
            N += 1
        if N > np.iinfo(renderbuffer.dtype).max:
          renderbuffer = fastremap.refit(renderbuffer, value=N, increase_only=True)

        fastremap.remap(img3d, remap, in_place=True)
        shade(renderbuffer, requested_bbox, img3d, bbox)

    fn = process
    if renumber and not (use_file or use_shared_memory):
      fn = process_renumber  

    download_chunks_threaded(
      meta, cache, mip, cloudpaths, 
      fn=fn, decode_fn=decode, fill_missing=fill_missing,
      progress=progress, compress_cache=compress_cache, 
      green=green, secrets=secrets, background_color=background_color
    )
  else:
    handle, renderbuffer = multiprocess_download(
      requested_bbox, mip, cloudpaths,
      meta, cache, compress_cache,
      fill_missing, progress,
      parallel, location, retain, 
      use_shared_memory=(use_file == False),
      order=order,
      green=green,
      secrets=secrets,
      background_color=background_color
    )
  
  out = VolumeCutout.from_volume(
    meta, mip, renderbuffer, 
    requested_bbox, handle=handle
  )
  if renumber:
    return (out, remap)
  return out

def download_single_voxel_unsharded(
  meta, cache, 
  requested_bbox, filename, 
  mip, fill_missing, compress_cache,
  secrets, renumber, background_color, 
):
  """Specialized function for rapidly extracting a single voxel."""
  locations = cache.compute_data_locations([ filename ])
  cachedir = 'file://' + os.path.join(cache.path, meta.key(mip))

  if locations["local"]:
    cloudpath = cachedir
    cache_enabled = False
  else:
    cloudpath = meta.cloudpath
    cache_enabled = cache.enabled

  chunk_bbx = Bbox.from_filename(filename)
  label, _ = download_chunk(
    meta, cache, 
    cloudpath, mip,
    filename, fill_missing,
    cache_enabled, compress_cache,
    secrets, background_color,
    partial(decode_single_voxel, requested_bbox.minpt - chunk_bbx.minpt)
  )

  if renumber:
    lbl = label[0,0,0,0]
    if lbl == background_color:
      return label, { lbl: lbl }
    else:
      remap = { lbl: 1 }
      label[0,0,0,0] = 1
      return label, remap

  return label

def multiprocess_download(
    requested_bbox, mip, cloudpaths,
    meta, cache, compress_cache,
    fill_missing, progress,
    parallel, location, 
    retain, use_shared_memory, order,
    green, secrets=None, background_color=0,
  ):
  cpd = partial(child_process_download, 
    meta, cache, mip, compress_cache, 
    requested_bbox, 
    fill_missing, progress,
    location, use_shared_memory,
    green, secrets, background_color
  )
  parallel_execution(
    cpd, cloudpaths, parallel, 
    progress=progress, 
    desc="Download",
    cleanup_shm=location,
    block_size=750,
  )

  shape = list(requested_bbox.size3()) + [ meta.num_channels ]

  if use_shared_memory:
    mmap_handle, renderbuffer = shm.ndarray(
      shape, dtype=meta.dtype, order=order, 
      location=location, lock=fs_lock
    )
  else:
    handle, renderbuffer = shm.ndarray_fs(
      shape, dtype=meta.dtype, order=order,
      location=location, lock=fs_lock,
      emulate_shm=False
    )    

  if not retain:
    if use_shared_memory:
      shm.unlink(location)
    else:
      os.unlink(location)

  return mmap_handle, renderbuffer

def child_process_download(
    meta, cache, mip, compress_cache, 
    dest_bbox, 
    fill_missing, progress,
    location, use_shared_memory, green,
    secrets, background_color, cloudpaths
  ):
  reset_connection_pools() # otherwise multi-process hangs

  shape = list(dest_bbox.size3()) + [ meta.num_channels ]

  if use_shared_memory:
    array_like, dest_img = shm.ndarray(
      shape, dtype=meta.dtype, 
      location=location, lock=fs_lock
    )
  else:
    array_like, dest_img = shm.ndarray_fs(
      shape, dtype=meta.dtype, 
      location=location, emulate_shm=False, 
      lock=fs_lock
    )

  if background_color != 0:
      dest_img[dest_bbox.to_slices()] = background_color

  def process(src_img, src_bbox):
    shade(dest_img, dest_bbox, src_img, src_bbox)
    if progress:
      # This is not good programming practice, but
      # I could not find a clean way to do this that
      # did not result in warnings about leaked semaphores.
      # progress_queue is created in common.py:initialize_progress_queue
      # as a global for this module.
      progress_queue.put(1)

  download_chunks_threaded(
    meta, cache, mip, cloudpaths,
    fn=process, decode_fn=decode, fill_missing=fill_missing,
    progress=False, compress_cache=compress_cache,
    green=green, secrets=secrets, background_color=background_color
  )

  array_like.close()

  return len(cloudpaths)

def download_chunk(
  meta, cache, 
  cloudpath, mip,
  filename, fill_missing,
  enable_cache, compress_cache,
  secrets, background_color,
  decode_fn
):
  (file,) = CloudFiles(cloudpath, secrets=secrets).get([ filename ], raw=True)
  content = file['content']

  if enable_cache:
    cache_content = next(compression.transcode(file, compress_cache))['content'] 
    CloudFiles('file://' + cache.path).put(
      path=filename, 
      content=(cache_content or b''), 
      content_type=content_type(meta.encoding(mip)), 
      compress=compress_cache,
      raw=bool(cache_content),
    )
    del cache_content

  if content is not None:
    content = compression.decompress(content, file['compress'])

  bbox = Bbox.from_filename(filename) # possible off by one error w/ exclusive bounds
  img3d = decode_fn(meta, filename, content, fill_missing, mip, 
                       background_color=background_color)
  return img3d, bbox

def download_chunks_threaded(
    meta, cache, mip, cloudpaths, fn, decode_fn,
    fill_missing, progress, compress_cache,
    green=False, secrets=None, background_color=0,
  ):
  """fn is the postprocess callback. decode_fn is a decode fn."""
  locations = cache.compute_data_locations(cloudpaths)
  cachedir = 'file://' + os.path.join(cache.path, meta.key(mip))

  def process(cloudpath, filename, enable_cache):
    labels, bbox = download_chunk(
      meta, cache, cloudpath, mip,
      filename, fill_missing,
      enable_cache, compress_cache,
      secrets, background_color,
      decode_fn
    )
    fn(labels, bbox)

  local_downloads = ( 
    partial(process, cachedir, os.path.basename(filename), False) for filename in locations['local'] 
  )
  remote_downloads = ( 
    partial(process, meta.cloudpath, filename, cache.enabled) for filename in locations['remote'] 
  )

  downloads = itertools.chain( local_downloads, remote_downloads )

  if progress and not isinstance(progress, str):
    progress = "Downloading"

  schedule_jobs(
    fns=downloads, 
    concurrency=DEFAULT_THREADS, 
    progress=progress,
    total=len(cloudpaths),
    green=green,
  )

def decode(
  meta, input_bbox, 
  content, fill_missing, 
  mip, background_color=0
):
  """
  Decode content from bytes into a numpy array using the 
  dataset metadata.

  If fill_missing is True, return an array filled with background_color
  if content is empty. Otherwise, raise an EmptyVolumeException
  in that case.

  Returns: ndarray
  """
  return _decode_helper(  
    chunks.decode, 
    meta, input_bbox, 
    content, fill_missing, 
    mip, background_color,
  )

def decode_unique(
  meta, input_bbox, 
  content, fill_missing, 
  mip, background_color=0
):
  """Gets the unique labels present in a given chunk."""
  return _decode_helper(  
    chunks.labels, 
    meta, input_bbox, 
    content, fill_missing, 
    mip, background_color,
  )

def decode_single_voxel(
  xyz, meta, input_bbox, 
  content, fill_missing, 
  mip, background_color=0
):
  """
  Specialized decode that for some file formats
  will be faster than regular decode when fetching
  a single voxel. Single voxel fetches are a common
  operation when e.g. people are querying the identity
  of a synapse or organelle location to build a database.
  """
  return _decode_helper(  
    partial(chunks.read_voxel, xyz),
    meta, input_bbox, 
    content, fill_missing, 
    mip, background_color,
  )

def _decode_helper(  
  fn, meta, input_bbox, 
  content, fill_missing, 
  mip, background_color=0,
):
  bbox = Bbox.create(input_bbox)
  content_len = len(content) if content is not None else 0

  if not content:
    if fill_missing:
      content = b''
    else:
      raise EmptyVolumeException(input_bbox)

  shape = list(bbox.size3()) + [ meta.num_channels ]

  try:
    return fn(
      content, 
      encoding=meta.encoding(mip), 
      shape=shape, 
      dtype=meta.dtype, 
      block_size=meta.compressed_segmentation_block_size(mip),
      background_color=background_color
    )
  except Exception as error:
    print(red('File Read Error: {} bytes, {}, {}, errors: {}'.format(
        content_len, bbox, input_bbox, error)))
    raise

def unique_unsharded(
  requested_bbox, mip, 
  meta, cache,
  fill_missing, progress,
  parallel,
  compress, 
  green=False, secrets=None,
  background_color=0
):
  """
  Accumulate all unique labels within the requested
  bounding box.
  """
  full_bbox = requested_bbox.expand_to_chunk_size(
    meta.chunk_size(mip), offset=meta.voxel_offset(mip)
  )
  full_bbox = Bbox.clamp(full_bbox, meta.bounds(mip))
  all_chunks = set(chunknames(
    full_bbox, meta.bounds(mip), 
    meta.key(mip), meta.chunk_size(mip), 
    protocol=meta.path.protocol
  ))
  retracted_bbox = requested_bbox.shrink_to_chunk_size(
    meta.chunk_size(mip), offset=meta.voxel_offset(mip)
  )
  retracted_bbox = Bbox.clamp(retracted_bbox, meta.bounds(mip))
  core_chunks = set(chunknames(retracted_bbox, meta.bounds(mip), meta.key(mip), meta.chunk_size(mip)))
  shell_chunks = all_chunks.difference(core_chunks)

  shape = list(requested_bbox.size3()) + [ meta.num_channels ]

  compress_cache = should_compress(meta.encoding(mip), compress, cache, iscache=True)

  all_labels = set()
  def process_core(labels, bbox):
    nonlocal all_labels
    all_labels |= set(labels)

  def process_shell(labels, bbox):
    nonlocal all_labels
    nonlocal requested_bbox
    crop_bbox = Bbox.intersection(requested_bbox, bbox)
    crop_bbox -= bbox.minpt
    labels = labels[ crop_bbox.to_slices() ]
    all_labels |= set(fastremap.unique(labels))

  download_chunks_threaded(
    meta, cache, mip, core_chunks, 
    fn=process_core, decode_fn=decode_unique, fill_missing=fill_missing,
    progress=progress, compress_cache=compress_cache, 
    green=green, secrets=secrets, background_color=background_color,
  )

  if len(shell_chunks) > 0:
    download_chunks_threaded(
      meta, cache, mip, shell_chunks, 
      fn=process_shell, decode_fn=decode, fill_missing=fill_missing,
      progress=progress, compress_cache=compress_cache, 
      green=green, secrets=secrets, background_color=background_color,
    )

  return all_labels

def unique_sharded(
  requested_bbox, mip,
  meta, cache, spec,
  compress, progress,
  fill_missing, background_color
):
  """
  Accumulate all unique labels within the requested
  bounding box.
  """
  full_bbox = requested_bbox.expand_to_chunk_size(
    meta.chunk_size(mip), offset=meta.voxel_offset(mip)
  )
  full_bbox = Bbox.clamp(full_bbox, meta.bounds(mip))
  core_bbox = requested_bbox.shrink_to_chunk_size(
    meta.chunk_size(mip), offset=meta.voxel_offset(mip)
  )
  core_bbox = Bbox.clamp(core_bbox, meta.bounds(mip))

  compress_cache = should_compress(meta.encoding(mip), compress, cache, iscache=True)

  chunk_size = meta.chunk_size(mip)
  grid_size = np.ceil(meta.bounds(mip).size3() / chunk_size).astype(np.uint32)

  reader = sharding.ShardReader(meta, cache, spec)
  bounds = meta.bounds(mip)

  all_gpts = list(gridpoints(full_bbox, bounds, chunk_size))
  core_gpts = list(gridpoints(core_bbox, bounds, chunk_size))

  code_map = {}
  all_morton_codes = compressed_morton_code(all_gpts, grid_size)
  for gridpoint, morton_code in zip(all_gpts, all_morton_codes):
    cutout_bbox = Bbox(
      bounds.minpt + gridpoint * chunk_size,
      min2(bounds.minpt + (gridpoint + 1) * chunk_size, bounds.maxpt)
    )
    code_map[morton_code] = cutout_bbox
  
  core_morton_codes = compressed_morton_code(core_gpts, grid_size)

  all_labels = set()
  
  for mcs in sip(core_morton_codes, 10000):
    core_chunkdata = reader.get_data(mcs, meta.key(mip), progress=progress)
    for zcode, chunkdata in core_chunkdata.items():
      cutout_bbox = code_map[zcode]
      labels = decode_unique(
        meta, cutout_bbox, 
        chunkdata, fill_missing, mip,
        background_color=background_color
      )
      all_labels |= set(labels)

  del core_chunkdata

  shell_morton_codes = set(all_morton_codes) - set(core_morton_codes)
  shell_chunkdata = reader.get_data(shell_morton_codes, meta.key(mip), progress=progress)
  for zcode, chunkdata in shell_chunkdata.items():
    cutout_bbox = code_map[zcode]
    labels = decode(
      meta, cutout_bbox, 
      chunkdata, fill_missing, mip,
      background_color=background_color
    )
    crop_bbox = Bbox.intersection(requested_bbox, cutout_bbox)
    crop_bbox -= cutout_bbox.minpt
    labels = fastremap.unique(labels[ crop_bbox.to_slices() ])
    all_labels |= set(labels)

  return all_labels

