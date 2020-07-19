# Self-hosted Disposable Email Service

Long story short, this is a self-hosted email service that allows you to create a disposable email address(es).
It uses AWS goodness and it costs next to nothing (unless you get bazillions of emails).

**At the moment this project is just a proof of concept. Eventually it will become real deal. Until then do not use it
for production purposes or to access sensitive data. You have been warned.**

## Installation

* register a domain
* [set up email receiving](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/receiving-email.html) 
* build and deploy stack


    sam build --use-container
    sam deploy --guided

* in AWS console set created ruleset as default
* [move out of the SES sandbox](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/request-production-access.html) (haven't done that yet so you're on your own)

## Usage

* go to Amazon Cognito console and create new user
* go to login url (returned in the cloudformation output) and login using user created in the previous step
* go to DynamoDB `<your-project-name>_tokens` table and copy id_token value
* run those requests to manage your disposable emails

Create new email address

    POST <your api url>/emails
    Accept: */*
    Cache-Control: no-cache
    Auth: <your id token>
    
    email=<some email address in your domain>&forward_to=<email address you want the messages to be forwared to>

List all email addresses

    GET <your api url>/emails
    Accept: */*
    Cache-Control: no-cache
    Auth: <your id token>

Delete email address

    DELETE <your api url>/emails/<some email address in your domain>
    Accept: */*
    Cache-Control: no-cache
    Auth: <your id token>

I know, it's not user friendly. Obviously the client part is missing. It will be added soon(ish), I'll start with web
and Slack clients.

## TODO:

* TODOs from the code
* log stuff like errors and other important information
* create whole bunch of metrics and alarms (plus send notifications when something goes wrong)
* handle errors gracefully
* split cloudformation template into separates stacks (api, mail forwarder, web site, slack client, etc.)
* move dependencies into a layer
* tests, tests, tests
* much better docs
* experiment with different regions
* check if there is a cloudformation way of setting default ruleset (SES thingy)
* forward actual email message (aka move out of the SES sandbox)
