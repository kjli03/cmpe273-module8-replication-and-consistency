# cmpe273-module8-replication-and-consistency

## Instructions:

```sh
python3 replication_simulation.py
```

## Architecture

```mermaid
flowchart LR
	Client["Client"]
	Primary["Primary Replica<br/>Inventory: authoritative"]
	Secondary["Secondary Replica<br/>Inventory: replicated copy"]

	Client -->|Read| Primary
	Client -->|Read| Secondary
	Client -->|Write inventory| Primary
	Primary -.->|Replicate update| Secondary
```

When replication is paused, the Primary queues updates until it resumes.

## Successful replication, stale-read test, and replicas converging after replication resumes:
![alt text](image.png)

## Reflection:
Reading from a replica will be faster than reading from the latest value. However, while reading from the replica can be faster to get a response, it may mean that the data is outdated and thus inaccurate. Reading from the latest value takes longer because we have to wait for the replication to confirm the read. This tradeoff between speed and accuracy means we should decide which is more important for the business needs of the service.