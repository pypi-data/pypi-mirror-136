from .compartment_reader import CompartmentReaderVer01 as SonataReaderDefault
from .compartment_writer import CompartmentWriterv01 as SonataWriterDefault
from .core import CompartmentReaderABC, CompartmentWriterABC
from bmtk.utils.io import bmtk_world_comm

try:
    comm = bmtk_world_comm.comm
    rank = comm.Get_rank()
    nhosts = comm.Get_size()

except Exception as exc:
    pass


class CompartmentReport(object):
    def __new__(cls, path, mode='r', adaptor=None, *args, **kwargs):
        if adaptor is not None:
            return adaptor
        else:
            if mode == 'r':
                return SonataReaderDefault(path, mode, **kwargs)
            else:
                return SonataWriterDefault(path, mode, **kwargs)

    @staticmethod
    def load(report):
        if isinstance(report, CompartmentReaderABC):
            return report
        elif isinstance(report, CompartmentWriterABC):
            raise AttributeError('Unable to load a CompartmentWriter object.')
        else:
            return CompartmentReport(report, mode='r')
