
import numpy as np

#this is a temporary solution and should instead be implemneted in qt
def scene(hat):
    import mayavi.mlab as mlab
    grid=hat.showData
    mlab.pipeline.volume(mlab.pipeline.scalar_field(grid),vmin=5, vmax=150)
    mlab.outline()
    mlab.show()

