
<h1 align="center">
  Clustered Index Benchmark
  <br>
</h1>

<h4 align="center">This Python project leverages the <a href="https://flask.palletsprojects.com/en/3.0.x/">Flask framework</a>, <a href="https://www.mysql.com/">MySQL database</a>, <a href="https://httpd.apache.org/docs/2.4/programs/ab.html">Apache Benchmark (ab)</a>, <a href="https://www.docker.com/">Docker</a>, <a href="https://faker.readthedocs.io/en/master/">Faker</a> for generating fake data, <a href="https://matplotlib.org/">Matplotlib</a> for visualizing results and <a hre="https://numpy.org/">NumPy</a> for numerical operations. The primary focus is on showcasing the benefits of utilizing a clustered index in database design. The project facilitates a clear demonstration of the impact of using a clustered index on database performance. It measures and compares the durations of data retrieval operations with and without the clustered index, providing insights into the efficiency gains achieved by employing proper indexing strategies.</h4>

<p align="center">
    <img src="./screenshot.png?raw=true" alt="screenshot">
</p>

<div align="center">
  <h3>
    <a href="">
      Benchmark Report
    </a>
</h3>
</div>


## How To Use

### 1. Clone the Repository

```bash
git clone https://github.com/DBDoco/clustered-index-benchmark.git
cd clustered-index-benchmark
```
### 2. Start Docker Compose

```bash
docker compose up
```

### 3. Check Endpoints
Verify that the endpoints are running by hitting the following URLs in your web browser:

<http://localhost:8001/read_with_index> <br>
<http://localhost:8001/read_without_index>

> If the localhost domain is not working, copy the IP address from the running terminal window.

### 4. Warm Up the App
Send some read requests to warm up the application using Apache Benchmark (ab). Open a new terminal window and run the following commands:

```bash
docker exec -it $(docker ps -a -q --filter name=experiment_project-web-server) ab -n 1000 -c 15 http://localhost:8001/write_with_index
docker exec -it $(docker ps -a -q --filter name=experiment_project-web-server) ab -n 1000 -c 15 http://localhost:8001/write_without_index
docker exec -it $(docker ps -a -q --filter name=experiment_project-web-server) ab -n 1000 -c 15 http://localhost:8001/read_with_index
docker exec -it $(docker ps -a -q --filter name=experiment_project-web-server) ab -n 1000 -c 15 http://localhost:8001/read_without_index
docker exec -it $(docker ps -a -q --filter name=experiment_project-web-server) ab -n 1 -c 1 http://localhost:8001/clear
```

> If chained commands don't run, just execute one by one.

### 5. Benchmark
Run the benchmark with the following commands:

```bash
docker exec -it $(docker ps -a -q --filter name=experiment_project-web-server) ab -n 500 -c 25 http://localhost:8001/write_with_index
docker exec -it $(docker ps -a -q --filter name=experiment_project-web-server) ab -n 500 -c 25 http://localhost:8001/write_without_index
docker exec -it $(docker ps -a -q --filter name=experiment_project-web-server) ab -n 1000 -c 25 http://localhost:8001/read_with_index
docker exec -it $(docker ps -a -q --filter name=experiment_project-web-server) ab -n 1000 -c 25 http://localhost:8001/read_without_index
```
> Feel free to adjust the numbers in the command to experiment with different scenarios. More requests generally yield better results.

### 6. Generate and View the Plot
Open the following URL in a web browser:

http://localhost:8001/get_plot

This will display a performance comparison plot illustrating the impact of clustered indexing.

### 7. Clear Data
To clear the data, hit the following endpoint:

http://localhost:8001/clear (using a browser, Postman, ab, etc.)
