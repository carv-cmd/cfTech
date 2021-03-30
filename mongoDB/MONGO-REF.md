## MongoDB Features/Reference

[`Mongo Monitoring Console`](https://cloud.mongodb.com/freemonitoring/cluster/NM5LDOHDT6Y5WJ7PMZTYBWRX3JMUZ6IX)

***
### Quick Finds
* [`MongoDB-Complete-Reference`](https://docs.mongodb.com/master/reference/)
* [`MongoDB Docs Glossary`](https://docs.mongodb.com/manual/reference/glossary/#glossary)
* [`MongoDB Limits and Thresholds`](https://docs.mongodb.com/master/reference/limits/#mongodb-limits-and-thresholds)
* [`Enable Access Control`](https://docs.mongodb.com/manual/tutorial/enable-authentication/index.html)

### Python-Mongo Interface / Drivers
  * [*PyMongo*](https://docs.mongodb.com/drivers/pymongo/)
    & [*Motor (Async Driver)*](https://docs.mongodb.com/drivers/motor/)
  * [*BSON.py*](https://pymongo.readthedocs.io/en/stable/api/bson/index.html#module-bson)
    & [*JSON.py*](https://docs.python.org/3/library/json.html)


### MongoDB Structure
* [**Document Database**](https://docs.mongodb.com/master/introduction/#document-database)

* [*Database*](https://docs.mongodb.com/master/core/databases-and-collections/#databases) >>
  [*Collections*](https://docs.mongodb.com/master/core/databases-and-collections/#collections) >>
  [*Documents*](https://docs.mongodb.com/master/core/document/#bson-document-format) >>
  [*BSONTypes*](https://docs.mongodb.com/manual/reference/bson-types/index.html)

***
### [*CRUD*](https://docs.mongodb.com/master/crud/#mongodb-crud-operations) Operations *create*, *read*, *update*, and *delete* documents.
* [**MongoDB CRUD Concepts Ethos**](https://docs.mongodb.com/master/core/crud/)
  

* [**Insert Documents**](https://docs.mongodb.com/master/tutorial/insert-documents/#insert-documents)
  * [*Insert Methods*](https://docs.mongodb.com/manual/reference/insert-methods/index.html)

    
* [**Query**](https://docs.mongodb.com/master/tutorial/query-documents/#query-documents)
  * [*Query on Embedded/Nested Documents*](https://docs.mongodb.com/master/tutorial/query-embedded-documents/)
  * [*Query an Array*](https://docs.mongodb.com/master/tutorial/query-arrays/)
  * [*Query an Array of Embedded Documents*](https://docs.mongodb.com/master/tutorial/query-array-of-documents/)
  * [*Project Fields to Return from Query*](https://docs.mongodb.com/master/tutorial/project-fields-from-query-results/)
  * [*Query for Null or Missing Fields¶*](https://docs.mongodb.com/master/tutorial/query-for-null-fields/)

    
* [**Update Documents**](https://docs.mongodb.com/master/tutorial/update-documents/)
  * [*Updates with Aggregation Pipeline*](https://docs.mongodb.com/master/tutorial/update-documents-with-aggregation-pipeline/)
  * [*Update Methods*](https://docs.mongodb.com/master/reference/update-methods/)


* [**Delete Documents**](https://docs.mongodb.com/master/tutorial/remove-documents/)
  * [*Delete Methods*](https://docs.mongodb.com/master/reference/delete-methods/)


* **Additional CRUD**
  * [*Bulk Write Operations*](https://docs.mongodb.com/manual/core/bulk-write-operations/index.html)
  * [*SQL to MongoDB Mapping Chart*](https://docs.mongodb.com/master/reference/sql-comparison/#sql-to-mongodb-mapping-chart)
  * [*Geospatial Queries*](https://docs.mongodb.com/master/tutorial/geospatial-tutorial/)
  * [*Text Search*](https://docs.mongodb.com/master/text-search/)
  * [*Read Concern*](https://docs.mongodb.com/master/reference/read-concern/)
  * [*Write Concern*](https://docs.mongodb.com/master/reference/write-concern/)  

***
### MongoDB Features

* [**SysAdmin**](https://docs.mongodb.com/master/administration/)
* [**Data Models**](https://docs.mongodb.com/master/core/data-modeling-introduction/)
* [**Transactions**](https://docs.mongodb.com/master/core/transactions/)
* [**Security**](https://docs.mongodb.com/master/security/)
* [**Storage**](https://docs.mongodb.com/master/storage/)
* [**FAQ**](https://docs.mongodb.com/master/faq/)


* [**Indexes**](https://docs.mongodb.com/manual/indexes/index.html) 
  support the efficient execution of queries in MongoDB. Without indexes, MongoDB 
  must perform a collection scan, i.e. scan every document in a collection, to select 
  those documents that match the query statement. If an appropriate index exists for a 
  query, MongoDB can use the index to limit the number of documents it must inspect.


* [**Change Streams**](https://docs.mongodb.com/manual/changeStreams/)
  useful when implementing Extract, Transform, and Load (ETL) services, cross-platform 
  synchronization, collaboration functionality, and notification services.


* [**Aggregation**](https://docs.mongodb.com/manual/aggregation/)
  operations process data records and return computed results. Group 
  values from multiple documents together, and can perform a variety 
  of operations on the grouped data to return a single result.
  * [*Aggregation Pipeline*](https://docs.mongodb.com/master/core/aggregation-pipeline/)
    * [*Views*](https://docs.mongodb.com/master/core/views/)
    * [*On-Demand Materialized Views*](https://docs.mongodb.com/master/core/materialized-views/)



* [**Replication \ Replica Sets**](https://docs.mongodb.com/master/replication/)
  in MongoDB is a group of mongod processes that maintain the same data set. 
  Replica sets provide redundancy and high availability, and are the basis for all production deployments. 
  * [*Replica Set Read and Write Semantics*](https://docs.mongodb.com/master/applications/replication/)
  * [*Replica Set Data Synchronization*](https://docs.mongodb.com/master/core/replica-set-sync/#replica-set-sync)
  

* [**Sharding**](https://docs.mongodb.com/master/sharding/#sharding-introduction)
   is a method for distributing data across multiple machines.
    * [*Zones*](https://docs.mongodb.com/master/core/zone-sharding/#zone-sharding)
    * [*Sharded Cluster Components*](https://docs.mongodb.com/master/core/sharded-cluster-components/#sharded-cluster-components)
      * Each [*Shard*](https://docs.mongodb.com/master/core/sharded-cluster-shards/)
        contains a subset of the sharded data, shards must be deployed as a replica set.
      * The [*mongos*](https://docs.mongodb.com/master/core/sharded-cluster-query-router/)
        acts as a query router, providing an interface between client applications and the sharded cluster. 
        Starting in MongoDB 4.4, mongos can support hedged reads to minimize latencies.
      * [*Config Servers*]()
        store metadata and configuration settings for the cluster, must be deployed as a replica set (CSRS).
        

***
### Command Line Utilities
* [*The MongoDB Tools Documentation*](https://docs.mongodb.com/database-tools/)
* [*Mongo Shell*](https://docs.mongodb.com/manual/reference/program/mongo/#mongo)
* [*mongofiles.cli*](https://docs.mongodb.com/database-tools/mongofiles/#mongodb-binary-bin.mongofiles)
* [*create.cli*](https://docs.mongodb.com/manual/reference/command/create/#dbcmd.create)
* [*insert.cli*](https://docs.mongodb.com/manual/reference/command/insert/index.html)
* [*mongod*](https://docs.mongodb.com/master/reference/program/mongod/#mongod)
