"""
Views for media management - Dashboard access.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from media.models import Media
from media.serializers import MediaSerializer
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import boto3
from django.conf import settings
import uuid


class DashboardMediaListView(APIView):
    """
    List and create media for the authenticated user's site.
    """
    permission_classes = [IsAuthenticated]
    # MultiPartParser lets the confirmation POST send a thumbnail file
    # alongside the video/image URL string fields.
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        responses=MediaSerializer(many=True),
        description="Get all media for the authenticated user's site",
        tags=['Dashboard - Media']
    )
    def get(self, request):
        """List all media"""
        try:
            # Get media that belongs to the user's site (not attached to specific content)
            media = Media.objects.filter(
                content_type__isnull=True,
                object_id__isnull=True
            ).order_by('-created_at')
            
            serializer = MediaSerializer(media, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        request=MediaSerializer,
        responses=MediaSerializer,
        description="Create a new media item (after uploading to presigned URL)",
        tags=['Dashboard - Media']
    )
    def post(self, request):
        """Create media record after presigned-URL upload.
        Accepts URL fields (image/video) plus an optional thumbnail file.
        """
        from media.serializers import MediaURLSerializer

        # Save thumbnail file to storage if provided as a file upload
        thumbnail_url = None
        thumb_file = request.FILES.get('thumbnail')
        if thumb_file:
            thumb_ext = thumb_file.name.split('.')[-1] if '.' in thumb_file.name else 'jpg'
            thumb_filename = f"uploads/{uuid.uuid4()}.{thumb_ext}"
            thumb_saved = default_storage.save(thumb_filename, ContentFile(thumb_file.read()))
            thumbnail_url = default_storage.url(thumb_saved)

        # Build data dict; for QueryDict use .dict() so it's mutable
        data = request.data.dict() if hasattr(request.data, 'dict') else dict(request.data)
        if thumbnail_url:
            data['thumbnail'] = thumbnail_url

        serializer = MediaURLSerializer(data=data)
        if serializer.is_valid():
            media = serializer.save()
            response_serializer = MediaSerializer(media)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardMediaDetailView(APIView):
    """
    Retrieve, update, or delete a media item.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self, pk):
        """Get media object"""
        try:
            return Media.objects.get(pk=pk)
        except Media.DoesNotExist:
            return None
    
    @extend_schema(
        responses=MediaSerializer,
        description="Get a specific media item",
        tags=['Dashboard - Media']
    )
    def get(self, request, pk):
        """Retrieve media"""
        media = self.get_object(pk)
        if not media:
            return Response(
                {'error': 'Media not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = MediaSerializer(media)
        return Response(serializer.data)
    
    @extend_schema(
        request=MediaSerializer,
        responses=MediaSerializer,
        description="Update a media item",
        tags=['Dashboard - Media']
    )
    def patch(self, request, pk):
        """Update media"""
        media = self.get_object(pk)
        if not media:
            return Response(
                {'error': 'Media not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = MediaSerializer(media, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        responses={204: None},
        description="Delete a media item",
        tags=['Dashboard - Media']
    )
    def delete(self, request, pk):
        """Delete media"""
        media = self.get_object(pk)
        if not media:
            return Response(
                {'error': 'Media not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        media.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetFeaturedMediaView(APIView):
    """
    Mark a media item as the featured one within its parent object (e.g. a project).
    Clears is_featured on all other media that share the same content_type + object_id,
    ensuring only one item is featured at a time per parent.
    If the media is not attached to any object, only the item itself is updated.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=MediaSerializer,
        description="Set this media item as featured (clears featured flag on siblings)",
        tags=['Dashboard - Media']
    )
    def post(self, request, pk):
        try:
            media = Media.objects.get(pk=pk)
        except Media.DoesNotExist:
            return Response({'error': 'Media not found'}, status=status.HTTP_404_NOT_FOUND)

        # If already featured, allow toggling off
        if media.is_featured:
            media.is_featured = False
            media.save(update_fields=['is_featured'])
            return Response(MediaSerializer(media).data)

        # Clear featured flag on all siblings in the same parent object
        if media.content_type_id and media.object_id:
            Media.objects.filter(
                content_type=media.content_type,
                object_id=media.object_id,
                is_featured=True,
            ).update(is_featured=False)

        media.is_featured = True
        media.save(update_fields=['is_featured'])
        return Response(MediaSerializer(media).data)


class DashboardMediaPresignedURLView(APIView):
    """
    Generate presigned URL for direct S3 upload.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='filename',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Original filename',
                required=True
            ),
            OpenApiParameter(
                name='content_type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='MIME type of the file',
                required=True
            ),
            OpenApiParameter(
                name='file_size',
                type=int,
                location=OpenApiParameter.QUERY,
                description='File size in bytes',
                required=True
            ),
        ],
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'upload_url': {'type': 'string'},
                    'file_key': {'type': 'string'},
                    'public_url': {'type': 'string'},
                }
            }
        },
        description="Generate a presigned URL for uploading media to S3",
        tags=['Dashboard - Media']
    )
    def get(self, request):
        """Generate presigned URL for upload"""
        filename = request.query_params.get('filename')
        content_type = request.query_params.get('content_type')
        file_size = request.query_params.get('file_size')
        
        if not all([filename, content_type, file_size]):
            return Response(
                {'error': 'filename, content_type, and file_size are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            file_size = int(file_size)
        except ValueError:
            return Response(
                {'error': 'file_size must be an integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size limits
        if content_type.startswith('image/'):
            max_size = 5 * 1024 * 1024  # 5MB for images
            if file_size > max_size:
                return Response(
                    {'error': 'Image files must be less than 5MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif content_type.startswith('video/'):
            max_size = 50 * 1024 * 1024  # 50MB for videos
            if file_size > max_size:
                return Response(
                    {'error': 'Video files must be less than 50MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Only image and video files are allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate unique file key
        ext = filename.split('.')[-1] if '.' in filename else ''
        file_uuid = str(uuid.uuid4())
        file_key = f"uploads/{file_uuid}.{ext}" if ext else f"uploads/{file_uuid}"
        
        try:
            # Get S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.STORAGES['default']['OPTIONS']['access_key'],
                aws_secret_access_key=settings.STORAGES['default']['OPTIONS']['secret_key'],
                endpoint_url=settings.STORAGES['default']['OPTIONS'].get('endpoint_url'),
                region_name=settings.STORAGES['default']['OPTIONS'].get('region_name', 'auto'),
            )
            
            bucket_name = settings.STORAGES['default']['OPTIONS']['bucket_name']
            
            # Generate presigned URL for PUT operation
            presigned_url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': file_key,
                    'ContentType': content_type,
                },
                ExpiresIn=3600  # URL expires in 1 hour
            )
            
            
            # Generate public URL
            custom_domain = settings.STORAGES['default']['OPTIONS'].get('custom_domain')
            if custom_domain:
                # Remove protocol if it's already in the custom domain
                if custom_domain.startswith('http://') or custom_domain.startswith('https://'):
                    public_url = f"{custom_domain}/{file_key}"
                else:
                    public_url = f"https://{custom_domain}/{file_key}"
            else:
                public_url = f"{settings.STORAGES['default']['OPTIONS'].get('endpoint_url')}/{bucket_name}/{file_key}"
            
            return Response({
                'upload_url': presigned_url,
                'file_key': file_key,
                'public_url': public_url,
                'content_type': content_type,
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to generate presigned URL: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DashboardMediaUploadView(APIView):
    """
    Upload media files through Django backend (proxy upload).
    Use this if direct S3 upload has CORS issues.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary'},
                    'alt': {'type': 'string'},
                    'caption': {'type': 'string'},
                }
            }
        },
        responses=MediaSerializer,
        description="Upload media file through Django backend",
        tags=['Dashboard - Media']
    )
    def post(self, request):
        """Upload media file"""
        file = request.FILES.get('file')
        
        if not file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        content_type = file.content_type
        is_image = content_type.startswith('image/')
        is_video = content_type.startswith('video/')
        
        if not is_image and not is_video:
            return Response(
                {'error': 'Only image and video files are allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size
        max_size = 5 * 1024 * 1024 if is_image else 50 * 1024 * 1024
        if file.size > max_size:
            return Response(
                {'error': f'{"Image" if is_image else "Video"} files must be less than {max_size // (1024 * 1024)}MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Generate unique filename for main file
            ext = file.name.split('.')[-1] if '.' in file.name else ''
            file_uuid = str(uuid.uuid4())
            filename = f"uploads/{file_uuid}.{ext}" if ext else f"uploads/{file_uuid}"
            
            # Save main file to S3
            saved_path = default_storage.save(filename, ContentFile(file.read()))
            file_url = default_storage.url(saved_path)
            
            # Handle optional thumbnail file
            thumbnail_url = None
            thumb_file = request.FILES.get('thumbnail')
            if thumb_file:
                thumb_ext = thumb_file.name.split('.')[-1] if '.' in thumb_file.name else 'jpg'
                thumb_uuid = str(uuid.uuid4())
                thumb_filename = f"uploads/{thumb_uuid}.{thumb_ext}"
                thumb_saved = default_storage.save(thumb_filename, ContentFile(thumb_file.read()))
                thumbnail_url = default_storage.url(thumb_saved)
            
            # Build media record
            media_data = {
                'image' if is_image else 'video': file_url,
                'alt': request.data.get('alt', file.name),
                'caption': request.data.get('caption', ''),
            }
            if thumbnail_url:
                media_data['thumbnail'] = thumbnail_url
            
            serializer = MediaSerializer(data=media_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response(
                {'error': f'Upload failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
