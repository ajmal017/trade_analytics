from django.contrib import admin
from .models import FeatureOperator,FeatureUnit,Category, Grading, SavedQueries, LinearTrends, GeneralFeature, GeneralFeatureValue, CombinesFeaturesEntry


admin.site.register(Category)
admin.site.register(Grading)
admin.site.register(SavedQueries)
admin.site.register(LinearTrends)



admin.site.register( GeneralFeature )
admin.site.register( GeneralFeatureValue )
admin.site.register( FeatureOperator )
admin.site.register( FeatureUnit )
admin.site.register( CombinesFeaturesEntry )



