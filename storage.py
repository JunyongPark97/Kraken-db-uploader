from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import os
from tempfile import SpooledTemporaryFile


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIA_LOCATION


class StaticStorage(S3Boto3Storage):
    location = settings.STATIC_LOCATION


class CustomS3Boto3Storage(S3Boto3Storage):

    location = settings.MEDIA_LOCATION

    """
    This is our custom version of S3Boto3Storage that fixes a bug in boto3 where the passed in file is closed upon upload.

    https://github.com/boto/boto3/issues/929
    https://github.com/matthewwithanm/django-imagekit/issues/391
    https://github.com/jschneier/django-storages/issues/382#issuecomment-377174808
    """

    def _save_content(self, obj, content, parameters):
        """
        We create a clone of the content file as when this is passed to boto3 it wrongly closes
        the file upon upload where as the storage backend expects it to still be open
        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified size
        content_autoclose = SpooledTemporaryFile()

        # Write our original content into our copy that will be closed by boto3
        content_autoclose.write(content.read())

        # Upload the object which will auto close the content_autoclose instance
        super(CustomS3Boto3Storage, self)._save_content(obj, content_autoclose, parameters)

        # Cleanup if this is fixed upstream our duplicate should always close
        if not content_autoclose.closed:
            content_autoclose.close()