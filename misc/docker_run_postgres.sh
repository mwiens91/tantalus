
docker rm /tantalus_postgres
docker run --name tantalus_postgres \
  -e POSTGRES_DB=$TANTALUS_POSTGRESQL_NAME \
  -e POSTGRES_USER=$TANTALUS_POSTGRESQL_USER \
  -e POSTGRES_PASSWORD=$TANTALUS_POSTGRESQL_PASSWORD \
  -p 5432:5432 postgres

