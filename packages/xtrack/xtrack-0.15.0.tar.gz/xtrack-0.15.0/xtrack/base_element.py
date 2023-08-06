# copyright ############################### #
# This file is part of the Xtrack Package.  #
# Copyright (c) CERN, 2021.                 #
# ######################################### #

from pathlib import Path
import numpy as np

import xobjects as xo
import xpart as xp

from .general import _pkg_root
from .interal_record import RecordIdentifier, RecordIndex, generate_get_record

start_per_part_block = """
   int64_t const n_part = LocalParticle_get__num_active_particles(part0); //only_for_context cpu_serial cpu_openmp
   #pragma omp parallel for                                       //only_for_context cpu_openmp
   for (int jj=0; jj<n_part; jj+=!!CHUNK_SIZE!!){                 //only_for_context cpu_serial cpu_openmp
    //#pragma omp simd
    for (int iii=0; iii<!!CHUNK_SIZE!!; iii++){                   //only_for_context cpu_serial cpu_openmp
      int const ii = iii+jj;                                      //only_for_context cpu_serial cpu_openmp
      if (ii<n_part){                                             //only_for_context cpu_serial cpu_openmp

        LocalParticle lpart = *part0;//only_for_context cpu_serial cpu_openmp
        LocalParticle* part = &lpart;//only_for_context cpu_serial cpu_openmp
        part->ipart = ii;            //only_for_context cpu_serial cpu_openmp

        LocalParticle* part = part0;//only_for_context opencl cuda
""".replace("!!CHUNK_SIZE!!", "128")

end_part_part_block = """
     } //only_for_context cpu_serial cpu_openmp
    }  //only_for_context cpu_serial cpu_openmp
   }   //only_for_context cpu_serial cpu_openmp
"""

def _handle_per_particle_blocks(sources):

    out = []
    for ii, ss in enumerate(sources):
        if isinstance(ss, Path):
            with open(ss, 'r') as fid:
                strss = fid.read()
        else:
            strss = ss

        if '//start_per_particle_block' in strss:

            lines = strss.splitlines()
            for ill, ll in enumerate(lines):
                if '//start_per_particle_block' in ll:
                    lines[ill] = start_per_part_block
                if '//end_per_particle_block' in ll:
                    lines[ill] = end_part_part_block

            # TODO: this is very dirty, just for check!!!!! 
            out.append('\n'.join(lines))
        else:
            out.append(ss)

    return out

def dress_element(XoElementData):

    DressedElement = xo.dress(XoElementData)
    assert XoElementData.__name__.endswith('Data')
    name = XoElementData.__name__[:-4]

    DressedElement.track_kernel_source = ('''
            /*gpukern*/
            '''
            f'void {name}_track_particles(\n'
            f'               {name}Data el,\n'
'''
                             ParticlesData particles,
                             int64_t flag_increment_at_element,
                /*gpuglmem*/ int8_t* io_buffer){
            LocalParticle lpart;
            lpart.io_buffer = io_buffer;

            int64_t part_id = 0;                    //only_for_context cpu_serial cpu_openmp
            int64_t part_id = blockDim.x * blockIdx.x + threadIdx.x; //only_for_context cuda
            int64_t part_id = get_global_id(0);                    //only_for_context opencl

            int64_t part_capacity = ParticlesData_get__capacity(particles);
            if (part_id<part_capacity){
                Particles_to_LocalParticle(particles, &lpart, part_id);
                if (check_is_active(&lpart)>0){
'''
            f'      {name}_track_local_particle(el, &lpart);\n'
'''
                }
                if (check_is_active(&lpart)>0 && flag_increment_at_element){
                        increment_at_element(&lpart);
                }
            }
        }
''')
    DressedElement._track_kernel_name = f'{name}_track_particles'
    DressedElement.track_kernel_description = {DressedElement._track_kernel_name:
        xo.Kernel(args=[xo.Arg(XoElementData, name='el'),
                        xo.Arg(xp.Particles.XoStruct, name='particles'),
                        xo.Arg(xo.Int64, name='flag_increment_at_element'),
                        xo.Arg(xo.Int8, pointer=True, name="io_buffer")])}
    DressedElement.iscollective = False

    def compile_track_kernel(self, save_source_as=None):
        context = self._buffer.context

        sources = []

        # Local particles
        sources.append(xp.gen_local_particle_api())

        # Tracker auxiliary functions
        sources.append(_pkg_root.joinpath("tracker_src/tracker.h"))

        # Internal recording
        sources.append(RecordIdentifier._gen_c_api())
        sources += RecordIdentifier.extra_sources
        sources.append(RecordIndex._gen_c_api())
        sources += RecordIndex.extra_sources

        sources += self.XoStruct.extra_sources
        sources.append(self.track_kernel_source)

        sources = _handle_per_particle_blocks(sources)

        context.add_kernels(sources=sources,
                kernels=self.track_kernel_description,
                save_source_as=save_source_as)


    def track(self, particles, increment_at_element=False):

        context = self._buffer.context
        if not hasattr(self, '_track_kernel'):
            if self._track_kernel_name not in context.kernels.keys():
                self.compile_track_kernel()
            self._track_kernel = context.kernels[self._track_kernel_name]

        if hasattr(self, 'io_buffer') and self.io_buffer is not None:
            io_buffer_arr = self.io_buffer.buffer
        else:
            io_buffer_arr=context.zeros(1, dtype=np.int8) # dummy

        self._track_kernel.description.n_threads = particles._capacity
        self._track_kernel(el=self._xobject, particles=particles,
                           flag_increment_at_element=increment_at_element,
                           io_buffer=io_buffer_arr)

    DressedElement.compile_track_kernel = compile_track_kernel
    DressedElement.track = track

    return DressedElement

# TODO Duplicated code with xo.DressedStruct, can it be avoided?
class MetaBeamElement(type):

    def __new__(cls, name, bases, data):
        XoStruct_name = name+'Data'
        if '_xofields' in data.keys():
            xofields = data['_xofields']
        else:
            for bb in bases:
                if hasattr(bb,'_xofields'):
                    xofields = bb._xofields
                    break

        if '_internal_record_class' in data.keys():
            xofields['_internal_record_id'] = RecordIdentifier
            if '_skip_in_to_dict' not in data.keys():
                data['_skip_in_to_dict'] = []
            data['_skip_in_to_dict'].append('_internal_record_id')

        XoStruct = type(XoStruct_name, (xo.Struct,), xofields)

        bases = (dress_element(XoStruct),) + bases
        new_class = type.__new__(cls, name, bases, data)

        XoStruct._DressingClass = new_class
        XoStruct.extra_sources = []

        if '_internal_record_class' in data.keys():
            new_class.XoStruct._internal_record_class = data['_internal_record_class']
            new_class._internal_record_class = data['_internal_record_class']
            new_class.XoStruct.extra_sources.extend(
                xo.context.sources_from_classes(xo.context.sort_classes(
                                            [data['_internal_record_class'].XoStruct])))
            new_class.XoStruct.extra_sources.append(
                generate_get_record(ele_classname=XoStruct_name,
                    record_classname=data['_internal_record_class'].XoStruct.__name__))

        return new_class

class BeamElement(metaclass=MetaBeamElement):
    _xofields={}

