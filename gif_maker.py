from PIL import Image
# ATTENTION
from wand.image import Image as wandImage
import time


def create_gif(images, base_size=1000, quality=30):
    # Add new frames into sequance
    for i in range(len(images)):
        ph = Image.open('photo/{}.jpg'.format(i))
        ratio = max(ph.size) / base_size
        ph = ph.resize((round(ph.size[0] / ratio), round(ph.size[1] / ratio)))
        ph.save('photo/{}{}.jpg'.format(i, i), quality=quality)

    with wandImage() as img:

        # Add new frames into sequance
        for i in range(len(images)):
            with wandImage(filename='photo/{}{}.jpg'.format(i, i), format='jpg') as ph:
                img.sequence.append(ph)

        # Create progressive delay for each frame
        for cursor in range(len(images)):
            with img.sequence[cursor] as frame:
                frame.delay = 30

        # Set layer type
        img.type = 'optimize'
        img.loop = 0

        img.save(filename='photo/erj.gif')


def shakalize(image_path, quality=5):
    img = Image.open(image_path)
    img.save('photo/shakal/shakal.jpg', quality=quality)


if __name__ == '__main__':
    # create_gif(['photo/0.jpg','photo/1.jpg','photo/2.jpg'])
    shakalize('photo/0.jpg')
