import dlib.cuda as cuda
import dlib

print(cuda.get_num_devices())
print(dlib.DLIB_USE_CUDA)