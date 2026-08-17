FROM golang:1.22-alpine AS build

WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /out/importer .

FROM alpine:3.20
RUN adduser -D -g '' importer
COPY --from=build /out/importer /usr/local/bin/importer
USER importer
ENTRYPOINT ["/usr/local/bin/importer"]
