from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    TrainerProfile, TrainerClient, TrainingProgram, TrainingSession, 
    Exercise, SessionExercise, NutritionPlan, Meal, MealFood, TrainerAppointment
)

@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'specialization', 'experience_years', 'hourly_rate', 'is_available')
    list_filter = ('specialization', 'is_available')
    search_fields = ('trainer__first_name', 'trainer__last_name', 'trainer__email', 'bio')

@admin.register(TrainerClient)
class TrainerClientAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'client', 'start_date', 'end_date', 'is_active', 'is_expired')
    list_filter = ('is_active', 'start_date')
    search_fields = ('trainer__first_name', 'trainer__last_name', 'client__first_name', 'client__last_name')
    date_hierarchy = 'start_date'
    readonly_fields = ('is_expired',)

class TrainingSessionInline(admin.TabularInline):
    model = TrainingSession
    extra = 1

@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'trainer', 'client', 'program_type', 'difficulty', 'start_date', 'end_date', 'is_active', 'is_expired')
    list_filter = ('program_type', 'difficulty', 'is_active', 'start_date')
    search_fields = ('title', 'trainer__first_name', 'trainer__last_name', 'client__first_name', 'client__last_name')
    date_hierarchy = 'start_date'
    readonly_fields = ('is_expired', 'days_left')
    inlines = [TrainingSessionInline]
    
    fieldsets = (
        (None, {'fields': ('trainer', 'client', 'title', 'description')}),
        (_('Program Detayları'), {'fields': ('program_type', 'difficulty', 'days_per_week')}),
        (_('Tarihler'), {'fields': ('start_date', 'end_date')}),
        (_('Durum'), {'fields': ('is_active', 'is_expired', 'days_left')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )

class SessionExerciseInline(admin.TabularInline):
    model = SessionExercise
    extra = 1
    ordering = ('order',)

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'program', 'day_of_week', 'duration_minutes')
    list_filter = ('day_of_week',)
    search_fields = ('title', 'program__title')
    inlines = [SessionExerciseInline]

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'muscle_group')
    list_filter = ('muscle_group',)
    search_fields = ('name', 'description', 'instructions')

class MealInline(admin.TabularInline):
    model = Meal
    extra = 1

@admin.register(NutritionPlan)
class NutritionPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'trainer', 'client', 'goal', 'start_date', 'end_date', 'is_active', 'is_expired')
    list_filter = ('goal', 'is_active', 'start_date')
    search_fields = ('title', 'trainer__first_name', 'trainer__last_name', 'client__first_name', 'client__last_name')
    date_hierarchy = 'start_date'
    readonly_fields = ('is_expired', 'days_left')
    inlines = [MealInline]
    
    fieldsets = (
        (None, {'fields': ('trainer', 'client', 'title', 'description')}),
        (_('Plan Detayları'), {'fields': ('goal', 'daily_calories', 'protein_grams', 'carbs_grams', 'fat_grams')}),
        (_('Tarihler'), {'fields': ('start_date', 'end_date')}),
        (_('Durum'), {'fields': ('is_active', 'is_expired', 'days_left')}),
        (_('Notlar'), {'fields': ('notes',)}),
    )

class MealFoodInline(admin.TabularInline):
    model = MealFood
    extra = 1

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('title', 'nutrition_plan', 'meal_type', 'time', 'calories')
    list_filter = ('meal_type',)
    search_fields = ('title', 'nutrition_plan__title')
    inlines = [MealFoodInline]

@admin.register(TrainerAppointment)
class TrainerAppointmentAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'client', 'date', 'start_time', 'end_time', 'status', 'duration_minutes', 'is_past')
    list_filter = ('status', 'date')
    search_fields = ('trainer__first_name', 'trainer__last_name', 'client__first_name', 'client__last_name')
    date_hierarchy = 'date'
    readonly_fields = ('duration_minutes', 'is_past')
