# Retrospective

A retrospective exhibition presents works from an extended period of
an artist's activity. Similarly, a retrospective compilation album is
assembled from a recording artist's past material, usually their
greatest hits. A television or newsstand special about an actor,
politician, or other celebrity will present a retrospective of the
subject's career highlights. A leading (usually elderly) academic may
be honored with a Festschrift, an honorary book of articles or a
lecture series relating topically to a retrospective of the honoree's
career. Celebrity roasts good-naturedly mock the career of the guest
of honor, often in a retrospective format.

This project seeks to create a 'retrospective' of Google News top hits.
Retrospective takes a search term and searches Google News multiple times
throughout a specified time range. It then parses this data and outputs a
title, summary, image, and link for use in a blog or other project. 

# Installation

**Install requirements**

```pip install -r requirements.txt```

**Upgrade Selenium**

```pip install -U selenium```

**Install ChromeDriver**

Download [ChromeDriver](https://sites.google.com/chromium.org/driver/) <br />

Save to /usr/local/bin/chromedriver

On a Mac, you will need to give security permissions to chromedriver: <br />
```cd /usr/local/bin``` <br />
```xattr -d com.apple.quarantine chromedriver```

Other OS may have similar procedures.

Once ChromeDriver is installed, Retrospective will keep it up to date with 
your current Chrome version

**Configure AWS CLI**

Retrospective sets up and uses AWS EC2 instances as proxies. 

You must [configure AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) if you haven't already.


# Tests
```python Retrospective/test.py```

# Usage

**Basic search for bioinformatics (console print out):**

```python Retrospective/Retrospective.py -t bioinformatics```

-t specifies search term

**Add articles to blog:**

```python Retrospective/Retrospective.py --repo /Users/my-user/my-website -t bioinformatics -c /content/blog -i /static/images --write-framework hugo```

--repo specifies absolute directory of your blog or website

-c specifies the content path - i.e. where the blog posts live

-i specifies the image path - i.e. where the images live

--write-framework specifies the framework that retrospective 
creates posts for. Options are only 'hugo' and None. None will print output.

**Adjust time period, window, and span:**

```python Retrospective/Retrospective.py -t bioinformatics -s 2 -p 6 -w 8```

-s specifies time span in which the total search takes place, in years. 
Specifying 2 will search up to 2 years in the past. Default is 2.

-p specifies time period in which separate queries will take place, in months.
Specifying 6 will create a new search every 6 months for the entire span. Default is 6.

-w specifies Time window in which individual queries take place, in weeks. 
Specifying 8 will look at all articles over an 8 week period for every 
individual search as specifies by the period and span. Default is 8.

**From Config**

Retrospective automatically populates a config file (retrospective.json by default) within the specified repository. This is intended to save your previous searches so that retrospective can be easily rerun and updated at a future time.

The --from-config option will carry out all previous searches saved in the config file, updated for the current date. You can manually edit the json file if you want to add more searches. This is the easiest way to manage using retrospective in a blog.

Example:

```python Retrospective/Retrospective.py --repo /Users/my-user/my-website -c /content/blog -i /static/images --write-framework hugo --from-config```

