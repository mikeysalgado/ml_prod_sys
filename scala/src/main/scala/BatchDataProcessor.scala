import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions.when
import java.util.Calendar
import java.util.Properties

object BatchDataProcessor {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession
      .builder
      // set number of cores to use in []
      .master("local[2]")
      .appName("BatchDataProcessor")
      .getOrCreate()

    // disable INFO log output from this point forward
    spark.sparkContext.setLogLevel("ERROR")

    import spark.implicits._


    spark.sparkContext.hadoopConfiguration.set("fs.s3a.access.key", "log-depositor")

    spark.sparkContext.hadoopConfiguration.set("fs.s3a.secret.key", "password1")

    spark.sparkContext.hadoopConfiguration.set("fs.s3a.endpoint", "http://127.0.0.1:9000")

    spark.sparkContext.hadoopConfiguration.set("fs.s3a.connection.ssl.enabled", "false")

    val logFileDF = spark.read.json("s3a://log-files/*.json")

    val spamEmails = logFileDF.filter(logFileDF("label") === "spam" && logFileDF("event") === "email::id::label::put")
    val allEmails = logFileDF.filter(logFileDF("event") === "email::id::label::put")


    // set the database name as appropriate
    val url = "jdbc:postgresql://127.0.0.1:5432/email_ingestion"
    val tableName = "emails"
    val props = new Properties()
    // set the following as appropriate
    props.setProperty("user", "ingestion_service")
    props.setProperty("password", "puppet-soil-SWEETEN")

    val postgresDF = spark.read
      .jdbc(url, tableName, props)


    val joinedEmails = postgresDF.join(spamEmails, Seq("email_id"), "left_outer")
    joinedEmails.show()
    val cleanedRowsEmails = joinedEmails.drop("email_folder", "event", "folder", "timestamp")
    val cleanedEmails = cleanedRowsEmails.withColumn("label", when($"label".isNotNull, $"label").otherwise("ham"))
    cleanedEmails.show()

    cleanedEmails
      .write
      .mode("overwrite")
      .json("s3a://cleaned-data/labeledEmails.json")

  }

}
