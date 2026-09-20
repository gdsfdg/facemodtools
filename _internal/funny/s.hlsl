StructuredBuffer<float3> base : register(t0);
StructuredBuffer<float3> key  : register(t1);
RWByteAddressBuffer rw_buffer : register(u1);

Texture1D<float4> IniParams : register(t120);
#define orig_stride IniParams[88].x

[numthreads(1, 1, 1)]
void main(uint3 DTid : SV_DispatchThreadID) {
    uint vertex = DTid.x;

    float3 basePos = base[vertex];
    float3 keyPos  = key[vertex];

    uint rwOffset = vertex * uint(orig_stride);

    float3 pos = asfloat(rw_buffer.Load3(rwOffset));
    pos += keyPos - basePos;
    rw_buffer.Store3(rwOffset, asuint(pos));
}