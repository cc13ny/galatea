import numpy as np

import sys
model_path = sys.argv[1]

pair_rescale = True
global_rescale = False

from pylearn2.utils import serial
print 'loading model...'
model = serial.load(model_path)
print 'done'

from pylearn2.config import yaml_parse
print 'loading dataset...'
dataset = yaml_parse.load(model.dataset_yaml_src)
print 'done'

import theano.tensor as T
from theano import function
model.make_pseudoparams()

def get_reconstruction_func():
    V = T.matrix()

    mf = model.e_step.variational_inference(V)
    H = mf['H_hat']
    S = mf['S_hat']
    Z = H*S
    recons = T.dot(Z,model.W.T)

    rval = function([V],recons)

    return rval

print 'making reconstruction function...'
f = get_reconstruction_func()
print 'done'

dataset.get_batch_design(model.nhid)

X = dataset.get_batch_design(50)
R = f(X)
if np.any(np.isnan(R)) or np.any(np.isinf(R)):
    mask = (np.isnan(R).sum(axis=1) + np.isinf(R).sum(axis=1)) > 0
    print float(mask.sum())/float(mask.shape[0])
    print R
    assert False

print 'mean squared error: ',np.square(X-R).mean()

Xt = dataset.get_topological_view(X)
Rt = dataset.get_topological_view(R)

from pylearn2.gui.patch_viewer import PatchViewer

num_patches = X.shape[0] * 2

import numpy as np

n = int( np.sqrt( num_patches ) )

rows = n
cols = n

if cols % 2 != 0:
    cols += 1

if rows * cols < num_patches:
    rows += 1

pv = PatchViewer( grid_shape = (rows, cols), patch_shape = Xt.shape[1:3], is_color = Xt.shape[3] > 1)

if global_rescale:
    scale = max(np.abs(Xt).max(),np.abs(Rt).max())
    Xt /= scale
    Rt /= scale
    scale = 1.

for i in xrange(X.shape[0]):
    x = Xt[i,:]
    r = Rt[i,:]

    if pair_rescale:
        scale = max(np.abs(x).max(),np.abs(r).max())

    assert scale != 0.0

    pv.add_patch( x / scale, rescale = False)
    pv.add_patch( r / scale, rescale = False)

pv.show()
