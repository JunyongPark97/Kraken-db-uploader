from django.db import models
import jsonfield
import random
import string


def random_name_generator(N):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))


###### Dataset Model ######

class KindOf(models.Model):
    """
    Dataset 의 종류입니다.
    Dataset model , 각각의 features model 과 1:N 관계입니다.
    """
    kinds = models.CharField(max_length=50)
    description = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return '{}'.format(self.kinds)

    class Meta:
        managed = False
        db_table = 'datasets_kindof'


class Dataset(models.Model):
    """
    데이터 메인 모델
    size, clothes(picture), wearing(pictures) 와 1:N / 버전관리를 위해 1:N 으로 선언하였습니다.

    ## Size queryset ex [from Size object]
    size_data = SizeOfShortSleeve.objects.filter(short_sleeve__name='test', version=1).last()
    ## Size queryset ex [from Dataset object]
    size_data = ShortSleeve.objects.get(name='test').sizes
    """
    kind_of = models.ForeignKey(KindOf, on_delete=models.PROTECT, related_name='dataset')
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    old_name = models.CharField(max_length=20, null=True, blank=True ,help_text='서버 만들기 전 참고가위해 만든 이름들')
    old_file_name = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        return '[{}] {}'.format(self.kind_of.kinds, self.name)

    class Meta:
        managed = False
        db_table = 'datasets_dataset'

    def save(self, *args, **kwargs):
        self.name = random_name_generator(8)
        super(Dataset, self).save(*args, **kwargs)


class RemarkTag(models.Model):
    """
    각 옷에대한 특징을 기록합니다
    ex: 재질, 늘어남, 색상 등
    """
    color = models.CharField(max_length=30, null=True, blank=True)
    material = models.CharField(max_length=100, null=True, blank=True)
    spread = models.BooleanField(default=None)
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE)
    
    class Meta:
        managed = False
        db_table = 'datasets_remarktag'
        
###### Dataset Model END ######


###### Utils Model ######

class DataVersion(models.Model):
    """
    Data 의 버전을 관리합니다.
    """
    version = models.FloatField()
    description = models.CharField(max_length=200, help_text='해당 버전의 기술적 목적을 적어주세요')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False, help_text='활성화된 버전. true 인 경우 앞으로 쌓는 데이터 버전으로 설정 됨')

    def __str__(self):
        return '[version {}] {}'.format(self.version, self.description)
    
    class Meta:
        managed = False
        db_table = 'utils_dataversion'


class SizeFeatures(models.Model):
    kind_of = models.ForeignKey(KindOf, on_delete=models.PROTECT, related_name='size_features')
    name = models.CharField(max_length=200, help_text='특징의 이름입니다')
    order = models.PositiveIntegerField(help_text='데이터 기입 순서에 사용합니다.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return '[{}] {}'.format(self.kind_of.kinds, self.name)

    class Meta:
        managed = False
        db_table = 'utils_sizefeatures'


class ClothesFeatures(models.Model):
    kind_of = models.ForeignKey(KindOf, on_delete=models.PROTECT, related_name='clothes_features')
    name = models.CharField(max_length=200, help_text='특징의 이름입니다')
    order = models.PositiveIntegerField(help_text='사진 촬영 순서에 사용합니다.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return '[{}] {}'.format(self.kind_of.kinds, self.name)

    class Meta:
        managed = False
        db_table = 'utils_clothesfeatures'


class WearingFeatures(models.Model):
    kind_of = models.ForeignKey(KindOf, on_delete=models.PROTECT, related_name='wearing_features')
    name = models.CharField(max_length=200, help_text='특징의 이름입니다')
    order = models.PositiveIntegerField(help_text='사진 촬영 순서에 사용합니다.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return '[{}] {}'.format(self.kind_of.kinds, self.name)

    class Meta:
        managed = False
        db_table = 'utils_wearingfeatures'
         
###### Utils Model END ######


###### Sizes Model ######

class Size(models.Model):
    """
    사이즈 모델
    version 으로 관리 (1차, 2차 ..)
    tags 로 features / value 관리
    """
    version = models.ForeignKey(DataVersion, on_delete=models.CASCADE, related_name='sizes') # 임시 CASCADE
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='sizes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'sizes_size'


class SizeTag(models.Model):
    """
    반팔 각 특징에 대한 사이즈입니다.
    tag 의 개념으로 사용합니다.
    """
    size_data = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='tags')
    features = models.ForeignKey(SizeFeatures, on_delete=models.CASCADE, related_name='sizes') # 임시 CASCADE
    value = models.FloatField(help_text='단위 cm / 잴 수 없으면 -1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False
        db_table = 'sizes_sizetag'

###### Sizes Model END ######

###### Pictures Model ######

def img_directory_path_clothes_picture(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s_%s.%s" % (instance.picture_data.dataset.name, key, ext)
    return 'picture/clothes/{}/{}/{}'.\
        format(instance.features.kind_of.kinds, instance.picture_data.version.version, filename)


def img_directory_path_wearing_picture(instance, filename):
    ext = filename.split('.')[-1]
    key = random_name_generator(6)
    filename = "%s_%s.%s" % (instance.picture_data.dataset.name, key, ext)
    return 'picture/wearing/{}/{}/{}'. \
        format(instance.features.kind_of.kinds, instance.picture_data.version.version, filename)


class ClothesPicture(models.Model):
    """
    데이터 옷 사진
    tags 에서 각 특징에 대해 관리합니다.
    이 모델과 Dataset 모델은 버전관리를 위해 N:1 관계입니다.
    """
    version = models.ForeignKey(DataVersion, on_delete=models.CASCADE, related_name='clothes_pictures')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='clothes_pictures')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return '[{}] name:{}'.format(self.version, self.dataset.name)

    class Meta:
        managed = False
        db_table = 'pictures_clothespicture'


class ClothesPictureTag(models.Model):
    """
    데이터 옷 사진 tag
    실제 이미지가 저장되는 모델
    features 에 하나의 옷 사진이 생성됩니다.
    """
    picture_data = models.ForeignKey(ClothesPicture, on_delete=models.CASCADE, related_name='tags')
    features = models.ForeignKey(ClothesFeatures, on_delete=models.CASCADE, related_name='clothes_picture_tags')
    picture = models.ImageField(upload_to=img_directory_path_clothes_picture)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'pictures_clothespicturetag'

    @property
    def image_url(self):
        return self.picture.url


class WearingPicture(models.Model):
    """
    데이터 옷 착용 사진
    tags 에서 각 특징에 대해 관리합니다.
    이 모델과 dataset 의 ShortSleeve 모델은 버전관리를 위해 N:1 관계입니다.
    """
    version = models.ForeignKey(DataVersion, on_delete=models.CASCADE, related_name='wearing_pictures')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='wearing_pictures')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'pictures_wearingpicture'


class WearingPictureTag(models.Model):
    """
    데이터 옷 착용 사진 tag
    실제 이미지가 저장되는 모델
    features 에 하나의 옷 사진이 생성됩니다.
    """
    picture_data = models.ForeignKey(WearingPicture, on_delete=models.CASCADE, related_name='tags')
    features = models.ForeignKey(WearingFeatures, on_delete=models.CASCADE, related_name='wearing_picture_tags')
    picture = models.ImageField(upload_to=img_directory_path_wearing_picture)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'pictures_wearingpicturetag'

###### Pictures Model END ######
