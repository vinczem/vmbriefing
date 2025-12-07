ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
  apk add --no-cache \
  python3 \
  py3-pip

# Copy data for add-on
COPY run.sh /
COPY app /app

RUN chmod a+x /run.sh

# Install python dependencies
RUN pip3 install --no-cache-dir -r /app/requirements.txt

CMD [ "/run.sh" ]
