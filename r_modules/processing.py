class Processing:

    def __init__(self, init_imgs):
        self.init_images = init_imgs
        self.width = init_imgs[0].width
        self.height = init_imgs[0].height
        self.extra_generation_params = {}
        self.bbox = []
        self.swapped_indexes = []


class ProcessingImg2Img(Processing):

    def __init__(self, init_img):
        super().__init__(init_img)
