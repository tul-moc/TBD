from pyflink.table import (EnvironmentSettings, TableEnvironment, TableDescriptor, 
                           DataTypes, Schema, FormatDescriptor)

env_settings = EnvironmentSettings.in_batch_mode()
table_env = TableEnvironment.create(env_settings)

table_1 = TableDescriptor.for_connector("filesystem") \
    .schema(Schema.new_builder()
            .column("user_id", DataTypes.INT())
            .column("movie_id", DataTypes.INT())
            .column("rating", DataTypes.INT())
            .column("timestamp", DataTypes.BIGINT())
            .build()) \
    .option("path", "u.data") \
    .format(FormatDescriptor.for_format("csv").option("field-delimiter", "\t").build()) \
    .build()

table_2 = TableDescriptor.for_connector("filesystem") \
    .schema(Schema.new_builder()
            .column("id", DataTypes.INT())
            .column("name", DataTypes.STRING())
            .build()) \
    .option("path", "u-mod.item") \
    .format(FormatDescriptor.for_format("csv").option("field-delimiter", "|").build()) \
    .build()

table_env.create_table("ratings", table_1)
ratings = table_env.from_path("ratings")

table_env.create_table("movies", table_2)
movies = table_env.from_path("movies")


filtered = ratings.filter(ratings.rating == 5)

grouped_count = filtered.group_by(filtered.movie_id) \
    .select(filtered.movie_id.alias("count_movie_id"), 
            filtered.rating.count.alias("rating_count")
            )


grouped_avg = ratings.group_by(ratings.movie_id) \
    .select(ratings.movie_id.alias("avg_movie_id"), 
            ratings.rating.avg.alias("rating_avg")
            )
    

grouped = grouped_count.join(grouped_avg) \
    .where(grouped_count.count_movie_id == grouped_avg.avg_movie_id) \
    .select(grouped_count.count_movie_id.alias("movie_id"), 
            grouped_count.rating_count, 
            grouped_avg.rating_avg
            )

joined = grouped.join(movies) \
    .where(grouped.movie_id == movies.id) \
    .select(grouped.movie_id, movies.name, grouped.rating_count, grouped.rating_avg)

sorted = joined.order_by(joined.rating_count.desc).fetch(10)

output_table = TableDescriptor.for_connector("print") \
    .schema(Schema.new_builder()
            .column("movie_id", DataTypes.INT())
            .column("name", DataTypes.STRING())
            .column("rating_count", DataTypes.BIGINT())
            .column("rating_avg", DataTypes.DOUBLE())
            .build()) \
    .build()

table_env.create_temporary_table("sink", output_table)
sorted.execute_insert("sink").wait()
