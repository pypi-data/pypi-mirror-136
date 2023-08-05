# automatically generated by the FlatBuffers compiler, do not modify

# namespace: gamma_api

import flatbuffers

class ResultItem(object):
    __slots__ = ['_tab']

    @classmethod
    def GetRootAsResultItem(cls, buf, offset):
        n = flatbuffers.encode.Get(flatbuffers.packer.uoffset, buf, offset)
        x = ResultItem()
        x.Init(buf, n + offset)
        return x

    # ResultItem
    def Init(self, buf, pos):
        self._tab = flatbuffers.table.Table(buf, pos)

    # ResultItem
    def Score(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(4))
        if o != 0:
            return self._tab.Get(flatbuffers.number_types.Float64Flags, o + self._tab.Pos)
        return 0.0

    # ResultItem
    def Attributes(self, j):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            x = self._tab.Vector(o)
            x += flatbuffers.number_types.UOffsetTFlags.py_type(j) * 4
            x = self._tab.Indirect(x)
            from .Attribute import Attribute
            obj = Attribute()
            obj.Init(self._tab.Bytes, x)
            return obj
        return None

    # ResultItem
    def AttributesLength(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(6))
        if o != 0:
            return self._tab.VectorLen(o)
        return 0

    # ResultItem
    def Extra(self):
        o = flatbuffers.number_types.UOffsetTFlags.py_type(self._tab.Offset(8))
        if o != 0:
            return self._tab.String(o + self._tab.Pos)
        return None

def ResultItemStart(builder): builder.StartObject(3)
def ResultItemAddScore(builder, score): builder.PrependFloat64Slot(0, score, 0.0)
def ResultItemAddAttributes(builder, attributes): builder.PrependUOffsetTRelativeSlot(1, flatbuffers.number_types.UOffsetTFlags.py_type(attributes), 0)
def ResultItemStartAttributesVector(builder, numElems): return builder.StartVector(4, numElems, 4)
def ResultItemAddExtra(builder, extra): builder.PrependUOffsetTRelativeSlot(2, flatbuffers.number_types.UOffsetTFlags.py_type(extra), 0)
def ResultItemEnd(builder): return builder.EndObject()
