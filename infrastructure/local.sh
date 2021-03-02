docker-compose up -d elasticsearch
sleep 5
docker-compose up -d
docker-compose logs -f