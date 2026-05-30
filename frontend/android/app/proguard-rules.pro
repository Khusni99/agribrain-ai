# Flutter specific
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.**  { *; }
-keep class io.flutter.util.**  { *; }
-keep class io.flutter.view.**  { *; }
-keep class io.flutter.**  { *; }
-keep class io.flutter.plugins.**  { *; }

# Keep JSON model classes (used with json_serializable / reflection)
-keep class com.example.agribrain_ai.** { *; }

# Keep Dio network models
-keep class com.example.agribrain_ai.data.models.** { *; }

# Keep Kotlin metadata
-keepattributes *Annotation*, InnerClasses
-dontnote kotlin.**, okhttp3.**, retrofit2.**
