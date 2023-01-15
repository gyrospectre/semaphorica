## Semaphorica
Helps you with data collection!

<img src="images/computer-shakehands.gif" />

Intended to be run on a schedule, Semaphorica takes a data source, normalises (and optionally further processes) the information collected, and then spits it out to one or more outputs. See the `modules` directory for supported platforms.

Originally written to help with the analysis of security threats in Splunk (when [Squyre](https://github.com/gyrospectre/squyre) can't be used!), it focusses on sources of this type. However, I'm sure it's useful for other applications. Maybe.

## Usage

To set things up the first time, just clone and install dependencies (venv is optional but highly recommended!).

```
git clone https://github.com/gyrospectre/semaphorica.git
cd semaphorica
virtualenv .venv
source .venv/bin/activate
pip install src/requirements.txt
```
Next, add your required sources to files in the `cfg` directory. A few examples have been provided to get you started - set `disabled` based on your needs.

Now you can run a one off collection as a test.
```
cd src
python semaphorica.py 
```

You can also scope a run to specific modules via command line args:

```
python semaphorica.py aws-networks tweetlist
```

## Checkpoints

Most data sources are streams. Like a Twitter feed or a web server log, events are continuously generated over time, usually with a timestamp.

Other sources are more static. Like a lookup table or list, they are updated periodically, but not in a stream. Think a file that is added to or removed from.

Semaphorica needs to handle these differently. For streamed sources, we maintain a checkpoint, which is just a pointer to which event we got up to for a given execution. When we next run a collection, we start from this point to avoid duplication. For lookup sources, a checkpoint doesn't make sense.

By default, AWS SSM is used to track checkpoints for each source. If you don't specify the `checkpoint_provider` key in your config, SSM is used.

If your source is a lookup type, simply add `checkpoint_provider: none` to your config.

If you need a checkpoint, then ensure that you have AWS credentials in your environment variables before you run! These cred need a minimum of `GetParameter` and `PutParameter` permissions. If you want to scope down further please do! See the example CloudFormation template in the `cloudformation` directory for some least privilege IAM.

## Credentials

Some providers, like Twitter and Splunk, require their own credentials. These are provided to Semaphoria via environment variables.

The variable name should be pretty obvious by taking a look at the module code, but for Twitter, the following env vars are needed (per the [Twitter docs](https://developer.twitter.com/en/docs/authentication/oauth-1-0a/obtaining-user-access-tokens)):

```
TWITTER_KEY
TWITTER_SECRET
TWITTER_TOKEN_KEY
TWITTER_TOKEN_SECRET
```

Splunk just needs a HEC token via `SPLUNK_TOKEN`.

## Message Format
All data is normalised to JSON, in the following format:
```
{
  "id": The event ID, if relevant.
  "received": The time the event was collected.
  "source_module": The module used.
  "source_identity": The identity associated with the event. e.g. Which account posted a tweet.
  "body": The actual event.
  "provenance": An ordered list of how the event got there. Right now, this is generally just the source platform.
  "tlp": A TLP label indicating the sharing boundaries of the data. See https://www.first.org/tlp/.
}
```

## Advanced and Real Life Usage
While Semaphorica is intended to be capable of processing the received data before sending on, this has not yet been implemented. I'll get to it eventually!

To get any meaningful value out of this, you'll need to run this on a schedule to keep things up to date. Whilst you can simply run with cron on a ..*shudder*.. server, I like to deploy the code to a serverless AWS Lambda function and then schedule a run every X hours via CloudWatch Events. See the `cloudformation` folder for an example template and associated README on how to achieve this.

This template will need to be tweaked for your environment, but with safer storage of secrets and everything defined as code ready for CI/CD, it should be a pretty good start.

<img src="images/welcome.gif" width="200" />

## License
MIT

## Author
[Bill Mahony](https://www.linkedin.com/in/bill-mahony-7651866/)
