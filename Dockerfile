FROM python:3.7.2-stretch
EXPOSE 8000
ENV PYTHONUNBUFFERED 1

# Update pip
RUN /usr/local/bin/python -m pip install --upgrade pip
# Install libgeos-dev using apt
RUN apt-get update
RUN apt-get install -y libgeos-dev
#Angular dependencies
# RUN apt-get -y install curl
# RUN curl -sL https://deb.nodesource.com/setup_12.x
# RUN apt-get -y install nodejs
# Download basemap (without spamming stdout)
RUN wget -q --show-progress --progress=bar:force:noscroll -O basemap-1.2.2rel.tar.gz https://github.com/matplotlib/basemap/archive/v1.2.2rel.tar.gz
# Install packages (basemap needs to installed separetly after numpy and matplotlib for no errors)
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN pip install ///basemap-1.2.2rel.tar.gz
# Make folders
RUN mkdir -p /app/broker/out/data_in
RUN mkdir -p /app/broker/out/data_out
RUN mkdir -p /app/broker/processed
RUN mkdir -p /tmp/results
RUN chmod -R 777 /tmp/results/
RUN mkdir /prsapp
RUN mkdir -p /static
COPY ./static/ /static/
COPY . /prsapp/
# Setting up angular project
# RUN npm install -y -g @angular/cli
# WORKDIR /prsapp/angular-frontend
# RUN npm install
# RUN ng build --prod --output-path ./static/angular-frontend/static/angular/ --output-hashing none
# RUN rm -rf node_modules
WORKDIR /prsapp
# Start
CMD ./init.sh
