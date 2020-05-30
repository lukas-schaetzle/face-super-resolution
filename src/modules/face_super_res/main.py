import numpy, torch, torchvision.transforms as transforms
from .model import Generator
from ..helper import getPath
from torchvision import utils

class FaceSuperResolutionNet():
  @torch.no_grad()
  def __init__(self):
    debug_log("Init face super resolution net")
    self.cuda = True if torch.cuda.is_available() else False
    self.device = torch.device('cuda' if self.cuda else 'cpu')
    self.generator = Generator().to(self.device)
    self.generator.eval()
    g_checkpoint = torch.load(
      getPath(__file__, "checkpoints/unalign_trained_generator_checkpoint.ckpt"),
      map_location='cuda:0' if self.cuda else torch.device('cpu')
    )
    self.generator.load_state_dict(g_checkpoint['model_state_dict'], strict=False)
    self.step = g_checkpoint['step']
    self.alpha = g_checkpoint['alpha']
    self.iteration = g_checkpoint['iteration']
    self.to_tensor = transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

  @torch.no_grad()
  def infer(self, input_img):
    transformed_image = self.to_tensor(input_img).unsqueeze(0).to(self.device)
    tensor_output = self.generator(transformed_image, self.step, self.alpha)
    tensor_img = torch.squeeze(0.5 * tensor_output + 0.5)
    # TODO: Fix transformation to PIL image (green pixels)
    return numpy.array(transforms.ToPILImage()(tensor_img.cpu()))
