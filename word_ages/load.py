# -*- coding: utf-8 -*-

import pickle
import requests, os, bs4, time
from multiprocessing import Pool


base_url = "https://www.merriam-webster.com/dictionary/"

def first_known_use(word):
    url = base_url + word
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, "html5lib")
    target_id = "first-known-use-explorer"
    if len(word)<3:
        return None
    try:
        date_div = soup.find_all("div", {"id" : target_id})
        date = date_div[0].find_all("div", {"class" : "new-text"})
        return date_div[0].find_all("div")[0].find("p").text.split(": ")[1]
    except:
        return None

def get_word_ages(text):
    start = time.time()
    words = text.split(' ')
    p = Pool(10)
    word_scores = p.map(first_known_use,words)
    p.terminate()
    p.join()
    end = time.time()
    delta = str(end-start)
    print('Took ' + delta + ' seconds')
    return word_scores

def usable_age(age):
    if not age:
        return None
    if "century" in age:
        if "before" in age:
            century = age.split(" ")[1][:-2]
            return int(century)*100
        else:
            century = age.split(" ")[0][:-2]
            return (int(century)*100)-50
    if "circa" in age:
            year = age.split(" ")[1]
            return int(year)
    else:
        return int(age)

def mean_age(ages):
    usable_ages = [usable_age(age) for age in ages if age]
    return sum(usable_ages)/len(usable_ages)

orwell_text = "Most people who bother with the matter at all would admit that the English language is in a bad way, but it is generally assumed that we cannot by conscious action do anything about it. Our civilization is decadent and our language — so the argument runs — must inevitably share in the general collapse. It follows that any struggle against the abuse of language is a sentimental archaism, like preferring candles to electric light or hansom cabs to aeroplanes. Underneath this lies the half-conscious belief that language is a natural growth and not an instrument which we shape for our own purposes."
sedaris_text = "I’ve been to Australia twice so far, but according to my father I’ve never actually seen it. He made this observation at the home of my cousin Joan, whom he and I visited just before Christmas last year, and it came on the heels of an equally aggressive comment. “Well,” he said, “David’s a better reader than he is a writer.” This from someone who hasn’t opened a book since “Dave Stockton’s Putt to Win,” in 1996. He’s never been to Australia, either. Never even come close."
