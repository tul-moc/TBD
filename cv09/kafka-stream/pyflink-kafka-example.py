from pyflink.table import (EnvironmentSettings, TableEnvironment, DataTypes, 
                           Schema, FormatDescriptor, TableDescriptor)
from pyflink.table.window import Slide
from pyflink.table.expressions import col, lit

env_settings = EnvironmentSettings.in_streaming_mode()
table_env = TableEnvironment.create(environment_settings=env_settings)

# Create the Kafka source table
table_env.create_temporary_table(
    'kafka_source',
    TableDescriptor.for_connector('kafka')
                .schema(Schema.new_builder()
                .column('title', DataTypes.STRING())
                .column('content', DataTypes.STRING())
                .column('category', DataTypes.ARRAY(DataTypes.STRING()))
                .column('img_count', DataTypes.INT().not_null())
                .column('original_created_date', DataTypes.STRING())
                .column('formatted_created_date', DataTypes.TIMESTAMP(3))
                .column('discussion_count', DataTypes.INT().not_null())
                .build())
        .option('topic', 'test-topic')
        .option('properties.bootstrap.servers', 'kafka:9092')
        .option('properties.group.id', 'flink-group')
        .option('scan.startup.mode', 'latest-offset')
        .format(FormatDescriptor.for_format('json')
                .option('timestamp-format.standard', 'ISO-8601')
                .build())
        .build())

data = table_env.from_path('kafka_source')
pipeline = table_env.create_statement_set()


#### Print actual article title to the console ####
article_titles = data.select(data.title)

table_env.create_temporary_table(
    'article_title_console_sink',
    TableDescriptor.for_connector("print")
        .schema(Schema.new_builder()
            .column('title', DataTypes.STRING())
            .build())
        .build())

pipeline.add_insert('article_title_console_sink', article_titles)


#### Detect articles with more than 100 discussion ####
#### Write them to file with format title;discussion_count ####
article_discussions = data.select(data.title, data.discussion_count) \
                        .filter(data.discussion_count > 100)

table_env.create_temporary_table(
    'article_discussion_file_sink',
     TableDescriptor.for_connector("filesystem")
        .schema(Schema.new_builder()
            .column('title', DataTypes.STRING())
            .column('discussion_count', DataTypes.INT())
            .build())
        .option('format', 'csv')
        .option('path', '/output/article_discussion.csv')
        .build()
)

pipeline.add_insert('article_discussion_file_sink', article_discussions)


#### Detect articles that are outside of date order ####
table_env.create_temporary_view("kafka_source_view", data)

out_of_order_sql = """
SELECT 
    title, 
    formatted_created_date,
    LAG(formatted_created_date, 1) OVER (ORDER BY formatted_created_date) AS prev_date
FROM kafka_source_view
"""

out_of_order_articles = table_env.sql_query(out_of_order_sql)

filtered_out_of_order_articles = out_of_order_articles.filter(
    out_of_order_articles.formatted_created_date < out_of_order_articles.prev_date
)

table_env.create_temporary_table(
    'out_of_order_file_sink',
    TableDescriptor.for_connector("filesystem")
        .schema(Schema.new_builder()
            .column('title', DataTypes.STRING())
            .column('formatted_created_date', DataTypes.TIMESTAMP(3))
            .column('prev_date', DataTypes.TIMESTAMP(3))
            .build())
        .option('format', 'csv')
        .option('path', '/output/out_of_order.csv')
        .build()
)

pipeline.add_insert('out_of_order_file_sink', filtered_out_of_order_articles)



#### Articles count in the window of 1 minute with 10 seconds slide ####
sliding_window = data.window(
    Slide.over(lit(60).seconds)
         .every(lit(10).seconds)
         .on(col('formatted_created_date'))
         .alias('window')
)

table_env.create_temporary_view("data_view", sliding_window)

agg_sql = """
SELECT 
    window_start,
    window_end,
    COUNT(title) AS article_count,
    SUM(CASE WHEN content LIKE '%válka%' THEN 1 ELSE 0 END) AS war_mentions
FROM data_view
GROUP BY window_start, window_end
"""

grouped_window = table_env.sql_query(agg_sql)
                        
table_env.create_temporary_table(
    'sliding_window_file_sink',
    TableDescriptor.for_connector("filesystem")
        .schema(Schema.new_builder()
            .column('window_start', DataTypes.TIMESTAMP(3))
            .column('window_end', DataTypes.TIMESTAMP(3))
            .column('article_count', DataTypes.BIGINT())
            .column('war_mentions', DataTypes.BIGINT())
            .build())
        .option('format', 'csv')
        .option('path', '/output/sliding_window.csv')
        .build()
)

pipeline.add_insert('sliding_window_file_sink', grouped_window)

pipeline.execute().wait()