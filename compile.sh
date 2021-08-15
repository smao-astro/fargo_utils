cd fargo3d
echo FLAG_PARALLEL=$FLAG_PARALLEL
make SETUP=$FLAG_SETUP \
        BIGMEM=$FLAG_BIGMEM \
        RESCALE=$FLAG_RESCALE \
        PROFILING=$FLAG_PROFILING \
        PARALLEL=$FLAG_PARALLEL \
        MPICUDA=$FLAG_MPICUDA \
        GPU=$FLAG_GPU \
        DEBUG=$FLAG_DEBUG \
        FULLDEBUG=$FLAG_FULLDEBUG \
        FARGO_DISPLAY=$FLAG_FARGO_DISPLAY \
        UNITS=$FLAG_UNITS \
        GHOSTSX=$FLAG_GHOSTSX \
        LONGSUMMARY=$FLAG_LONGSUMMARY
