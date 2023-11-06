# Cloud Computing Project 2 - PaaS
Educators often record classroom sessions, containing valuable untapped data. Identifying students in these recordings manually is time-consuming and impractical, especially in larger settings. The "PaaS for CSE 546: Cloud Computing" project aims to create a Smart Classroom Assistant using AWS. It automates student recognition in uploaded videos, providing a swift, accurate tool for educators to access academic information efficiently.

## Built With

* [AWS Lambda](https://aws.amazon.com/lambda/)
* [Amazon S3](https://aws.amazon.com/s3/)
* [Amazon DynamoDB](https://aws.amazon.com/dynamodb/)
* [Amazon ECR](https://aws.amazon.com/ecr/)
* [ffmpeg](https://ffmpeg.org/)
* [face_recognition](https://pypi.org/project/face-recognition/)

## Getting Started

The following instructions will guide you through the setup and deployment process.

### Prerequisites

- An AWS account with access to Lambda, S3, DynamoDB, and ECR.
- Docker installed on your machine.
- Create the Input and Output S3 buckets and setup the AWS DynamoDB.
- Configure AWS ECR for storing the docker images in the repository.
- The AWS CLI installed and configured.

### Installation

1. Clone the repo: git clone https://github.com/purulokendrasingh/CC-Project2
2. Insert your AWS credentials into the `handler.py` file.
3. Configure your S3 bucket and DynamoDB table details in `handler.py`.
4. Create an ECR repository, configure the Lambda handler, build and tag the Docker image, and upload it to your ECR repository.
5. Create the Lambda function with the ECR image and set up the S3 trigger for the input bucket.
6. Run the workload generator.
   ```bash
   python3 workload.py
   ```

## Usage

To aid in the testing process, a standard set of 100 short video files is supplied as an image dataset and used as follows:

- Upload video files to the designated S3 input bucket.
- The Lambda function will automatically be triggered to process the videos.
- Check the output S3 bucket for the resulting CSV files containing academic information.

| Resource | ID |
| -------- | --- |
| Input Bucket Tier | inputbucket-cc2 |
|Output Bucket Tier | outputbucket-cc2 |
|Dynamo DB Table Name | Students |

## Design and Implementation

### Architecture
The system's architecture is segmented into two primary tiers: the Web Tier (front-end) and the App Tier (back-end).
•	Web Tier: This layer provides the user interface that facilitates interaction with the application. To enhance user experience and ensure smooth operations, we have integrated two AWS S3 buckets into this tier:
1.	Input Bucket: Allows users to upload classroom videos.
2.	Output Bucket: Serves as a repository for academic data linked to recognized students.
•	App Tier: The core logic and computational aspects reside in this tier, implemented primarily through AWS Lambda - a serverless compute service. Unlike traditional cloud services that necessitate server provisioning, Lambda operates based on event triggers, making it both cost-effective and highly scalable. In the context of this application, an event is predominantly the uploading of a video to the S3 bucket. However, AWS Lambda can also respond to a variety of other events, like changes in Amazon DynamoDB or HTTP requests via the Amazon API Gateway.
Upon the uploading of a video to the input S3 bucket, the Lambda function is invoked. Its initial task is the extraction of frames from the input video, achieved using the ffmpeg multimedia framework. Based on the application's current configuration, a single frame is extracted, but this can be adjusted depending on computational availability and specific requirements. Subsequent to frame extraction, the face recognition process commences, utilizing the Python face recognition library. When a face is successfully identified, a label is generated. This label aids in querying AWS DynamoDB to fetch academic data related to the recognized student. The retrieved information is then uploaded to the output S3 bucket in the form of a text file. Post-upload, a cleanup process is initiated, removing the extracted frames and gracefully terminating the Lambda function.
The Lambda function operates within a custom Docker container image. This image comes pre-installed with both the ffmpeg and face recognition libraries, ensuring optimal execution without the need for additional installations or configurations.

### Autoscaling
Explain in detail how your design and implementation support automatic scale-up and -down on demand.
AWS Lambda's infrastructure is architected for automatic scalability, adapting dynamically to variable workloads. Upon a function invocation, AWS Lambda efficiently allocates the necessary resources for request handling, runs the function's code, and subsequently releases those resources. This dynamic resource allocation model ensures both cost efficiency, by utilizing resources only when required, and scalability, by adapting to the prevailing demand.
Furthermore, AWS Lambda offers granular scaling configurations, enabling users to delineate both the minimum and maximum instance counts for function executions. Additionally, the rate at which the function scales in reaction to surging traffic can be tailored. One can also set provisioned concurrency, which guarantees the constant availability of a designated number of instances, effectively curtailing cold start durations of functions.
For the scope of this project, we adhered to the default concurrency settings provided by Lambda. By doing so, Lambda oversees the expansion of execution environments up to the account's preset concurrency threshold. It's noteworthy that, by standard, Lambda endows an account with an aggregate concurrency cap of 1,000 for all functions within a specific region.

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/gremlin97"><img src="https://avatars.githubusercontent.com/u/22516287?v=4" width="100px;" alt=""/><br /><sub><b>Kunal Sunil Kasodekar</b></td>
      <td align="center"><a href="https://github.com/purulokendrasingh"><img src="https://avatars.githubusercontent.com/u/29207426?v=4" width="100px;" alt=""/><br /><sub><b>Puru Lokendra Singh</b></td>
      <td align="center"><a href="https://github.com/jashkahar"><img src="https://avatars.githubusercontent.com/u/47451302?v=4" width="100px;" alt=""/><br /><sub><b>Jash Pramod Kahar</b></a></td>
    </tr>
  </tbody>
</table>