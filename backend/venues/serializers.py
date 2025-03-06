from rest_framework import serializers
from .models import Venue, VenueImage, VenueReview

class VenueImageSerializer(serializers.ModelSerializer):
    """
    구장 이미지 시리얼라이저
    """
    class Meta:
        model = VenueImage
        fields = ('id', 'image', 'description')

class VenueReviewSerializer(serializers.ModelSerializer):
    """
    구장 리뷰 시리얼라이저
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = VenueReview
        fields = ('id', 'user', 'user_username', 'rating', 'comment', 'created_at')
        read_only_fields = ('user',)
    
    def create(self, validated_data):
        user = self.context['request'].user
        venue_id = self.context['venue_id']
        venue = Venue.objects.get(id=venue_id)
        
        review = VenueReview.objects.create(
            user=user,
            venue=venue,
            **validated_data
        )
        return review

class VenueSerializer(serializers.ModelSerializer):
    """
    구장 시리얼라이저
    """
    images = VenueImageSerializer(many=True, read_only=True)
    reviews = VenueReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Venue
        fields = ('id', 'name', 'address', 'latitude', 'longitude', 'description',
                  'surface_type', 'size', 'image', 'hourly_rate', 'opening_time',
                  'closing_time', 'has_parking', 'has_shower', 'has_locker',
                  'images', 'reviews', 'average_rating')
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)

class VenueListSerializer(serializers.ModelSerializer):
    """
    구장 목록 시리얼라이저 (간략한 정보)
    """
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Venue
        fields = ('id', 'name', 'address', 'surface_type', 'size', 'image',
                  'hourly_rate', 'average_rating', 'review_count')
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)
    
    def get_review_count(self, obj):
        return obj.reviews.count() 