# -*- coding: utf-8 -*-
"""
English Vocabulary Trainer – Streamlit-Version
Alle Vokabeln aus "E-WAM-10 Vocabulary Sheet, Unit 1: Identity" (Seiten 1–3).

Start:
    pip install streamlit pandas
    streamlit run english_vokabeltrainer_streamlit.py

Funktionen:
  * 63 Vokabeln & Wendungen in 5 Kapiteln (frei kombinierbar)
  * 315 Lückensätze (5 pro Vokabel, darunter der Beispielsatz vom Vokabelblatt)
  * 5 Lernmodi: Eintippen, Multiple Choice, Karteikarten,
    Lückensatz (Eintippen), Lückensatz (Auswahl)
  * Leitner-Karteikasten (5 Boxen) mit Wiederholungsterminen (Spaced Repetition)
  * Falsche Vokabeln kommen in der Sitzung automatisch bald wieder
  * Schrittweise Hinweise, "Als richtig werten", Zeitlimit, Favoriten
  * Vokabelliste mit Suche/Filter, Statistik, 7-Tage-Diagramm, Lerntage-Serie
  * Fortschritt wird in "englisch_fortschritt.json" gespeichert
    (zusätzlich: Export/Import als Datei, z. B. für Streamlit Cloud)
"""

import copy
import html
import inspect
import json
import random
import re
import time
from datetime import date, timedelta
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="English Vocabulary Trainer", page_icon="🇬🇧", layout="wide")

APP_TITLE = "English Vocabulary Trainer"
try:
    _BASE_DIR = Path(__file__).resolve().parent
except NameError:
    _BASE_DIR = Path.cwd()
SAVE_FILE = _BASE_DIR / "englisch_fortschritt.json"


# ----------------------------------------------------------------------------
# VOKABELN & LÜCKENSÄTZE
#   ## Kapitel
#   Englisch :: Deutsch [:: akzeptierte englische Antworten, getrennt mit |]
#   > Satz mit {Lösung|weitere richtige Lösung} @ eigener deutscher Hinweis (optional)
#   Die erste Lösung in { } ist die gesuchte Form. Jeder Satz hat genau eine Lücke.
# ----------------------------------------------------------------------------
RAW_DATA = r"""
## 1 Identity – who we are
identity :: Identität
> Our {identity} is shaped by many different things.
> Moving to another country can change a person's sense of {identity}.
> Your name is an important part of your {identity}.
> Many teenagers are still searching for their own {identity}.
> Language and {identity} are often closely connected.
background :: Herkunft, Hintergrund
> People from different {backgrounds} can become close friends.
> Our school welcomes students from every social {background}.
> She is proud of her Turkish family {background}.
> His {background} does not decide what he can achieve.
> The teacher wants to learn more about her pupils' cultural {backgrounds}.
roots (pl.) :: Wurzeln :: roots
> The speaker in “I Come From” is proud of his {roots}.
> She travelled to Ghana to discover her family's {roots}.
> Even after twenty years abroad, he has not forgotten his {roots}.
> My grandparents have Polish {roots}.
> Learning her mother's language helps Lina stay close to her {roots}.
upbringing :: Erziehung
> Our {upbringing} teaches us our first values.
> He had a very strict {upbringing}.
> Because of her religious {upbringing}, she knows many old prayers.
> My parents gave me a happy and safe {upbringing}.
> A person's {upbringing} can have a strong effect on their behaviour.
heritage :: (kulturelles) Erbe :: heritage | cultural heritage
> Many families try to keep their cultural {heritage} alive.
> The old songs are part of our {heritage}.
> The museum helps to protect the region's {heritage}.
> She is learning traditional dances to celebrate her Indian {heritage}.
> This castle is an important part of the country's cultural {heritage}.
culture :: Kultur
> Food is an important part of every {culture}.
> I would like to learn more about Japanese {culture}.
> Music and art are important parts of a country's {culture}.
> In some {cultures}, people take off their shoes before entering a house.
> Living abroad helped him to understand a different {culture}.
tradition :: Tradition, Brauch :: tradition
> A Sunday roast is a British {tradition}.
> In our family, it is a {tradition} to cook together on New Year's Eve.
> Every village here has its own {traditions}.
> The school wants to keep this old {tradition} alive.
> Giving presents at Christmas is a popular {tradition}.
values (pl.) :: Werte :: values
> Honesty is one of the {values} I learned at home.
> Respect and fairness are important {values} in our class.
> My best friend and I share the same {values}.
> Parents often try to pass on their {values} to their children.
> The two parties stand for very different {values}.
nationality :: Staatsangehörigkeit
> Some people have more than one {nationality}.
> Please write your name, age and {nationality} on the form.
> She has British {nationality}, but she was born in Spain.
> Students of more than twenty different {nationalities} attend this school.
> “What is your {nationality}?” – “I am German.”
community :: Gemeinschaft
> A strong {community} helps people feel at home.
> The whole {community} helped to rebuild the playground.
> He does volunteer work because he wants to give something back to his {community}.
> After a few months, they felt like part of the {community}.
> The festival brings the local {community} together.
to belong (to) :: (dazu)gehören :: belong | to belong | belong to | to belong to
> Everybody wants to feel that they {belong}.
> This bike {belongs} to my sister.
> Do you {belong} to a sports club?
> After a few weeks at the new school, he felt that he {belonged} there.
> These keys must {belong} to somebody in this room.
sense of belonging :: Zugehörigkeitsgefühl
> A sports club can give young people a {sense of belonging}.
> Singing in the choir gives me a strong {sense of belonging}.
> New students need time to develop a {sense of belonging}.
> Shared traditions can create a {sense of belonging}.
> Without friends at school, it is hard to feel a {sense of belonging}.
to fit in :: sich anpassen, dazugehören :: fit in | to fit in
> The boy in “Tiresias” does not {fit in} at the bus stop.
> She bought the same shoes as her classmates because she wanted to {fit in}.
> It took him a while to {fit in} at his new school.
> You do not have to change who you are just to {fit in}.
> At first, I felt that I did not {fit in} with the others.
to stand out :: auffallen, sich abheben :: stand out | to stand out
> Some people dye their hair purple to {stand out}.
> Her bright yellow coat made her {stand out} in the crowd.
> If you want your application to {stand out}, add some personal details.
> He is so tall that he always {stands out} in class photos.
> Some teenagers wear unusual clothes because they like to {stand out}.
to be shaped by :: geprägt werden von :: to be shaped by | be shaped by | shaped by
> We are {shaped by} the people around us.
> Our personality is {shaped by} our experiences.
> His view of the world was {shaped by} his childhood in a small village.
> Many of our habits are {shaped by} our family.
> The city's culture has been {shaped by} people from all over the world.
to influence sb./sth. :: beeinflussen :: influence | to influence
> Social media {influences} how teenagers see themselves.
> Friends can strongly {influence} our decisions.
> Advertising tries to {influence} what we buy.
> The weather often {influences} my mood.
> Her art teacher {influenced} her choice of career.
role model :: Vorbild
> My grandma has always been my {role model}.
> Famous athletes are {role models} for many children.
> Parents should try to be a good {role model} for their children.
> He sees his older brother as his {role model}.
> Do you have a {role model} who inspires you?
peer pressure :: Gruppenzwang
> {Peer pressure} can make teenagers do things they do not want to do.
> He only started smoking because of {peer pressure}.
> It is not always easy to resist {peer pressure}.
> Some students buy expensive clothes because of {peer pressure}.
> {Peer pressure} is often especially strong during the teenage years.
self-confidence :: Selbstbewusstsein
> The speaker in “Roar” gains {self-confidence}.
> Playing in a band has given me more {self-confidence}.
> After failing the test twice, he lost some of his {self-confidence}.
> Praise can help to build a child's {self-confidence}.
> She walked onto the stage full of {self-confidence}.
to express yourself :: sich ausdrücken :: express yourself | to express yourself
> Music is a great way to {express yourself}.
> Painting allows you to {express yourself} without using words.
> Do not be afraid to {express yourself} openly in this group.
> You can {express yourself} through the clothes you wear.
> If you learn more words, you will be able to {express yourself} more clearly.
stereotype :: Stereotyp, Klischee :: stereotype
> A profile picture can easily lead to {stereotypes}.
> It is a {stereotype} that all British people drink tea all day.
> The film is full of {stereotypes} about teenagers.
> The idea that girls are bad at maths is a harmful {stereotype}.
> We should question {stereotypes} instead of simply believing them.
prejudice :: Vorurteil
> {Prejudice} often comes from not knowing other people.
> Getting to know each other can help to reduce {prejudice}.
> He has to fight against other people's {prejudices}.
> Judging someone before you have even met them is a sign of {prejudice}.
> Many immigrants still experience {prejudice} in everyday life.
diversity :: Vielfalt
> {Diversity} makes a class more interesting.
> Our city is known for its cultural {diversity}.
> The company wants more {diversity} in its teams.
> The festival celebrates the {diversity} of our community.
> There is a great {diversity} of languages at our school.
to identify with sb./sth. :: sich identifizieren mit :: identify with | to identify with
> Many fans {identify with} the message of “Roar”.
> I can easily {identify with} the main character of the novel.
> Many young people {identify with} the music they listen to.
> He grew up in France, but he does not really {identify with} French culture.
> It is hard to {identify with} a hero who never makes mistakes.

## 2 Describing people and attitudes
open-minded :: aufgeschlossen
> Travelling can make you more {open-minded}.
> My aunt is very {open-minded} and loves hearing new ideas.
> An {open-minded} person listens to different opinions.
> Try to be {open-minded} when you taste food from other countries.
> Our new teacher is {open-minded} about trying different methods.
insecure :: unsicher
> The boy in the poem feels {insecure} about his looks.
> Many teenagers feel {insecure} about their bodies.
> Negative comments online can make people feel {insecure}.
> She seems confident, but deep down she is quite {insecure}.
> I used to be very {insecure} about speaking English in class.
(to be) proud of :: stolz sein auf :: proud of | to be proud of | be proud of
> The speaker is {proud of} his British passport.
> My parents are very {proud of} me.
> You should be {proud of} what you have achieved.
> She is {proud of} her Italian roots.
> We are all {proud of} our school team.
ambitious :: ehrgeizig
> She is {ambitious} and wants to study medicine.
> He is an {ambitious} young player who wants to turn professional.
> My sister is so {ambitious} that she studies even during the holidays.
> {Ambitious} people often set themselves difficult goals.
> Running a marathon after only two months of training is a very {ambitious} plan.
easy-going :: locker, gelassen :: easy-going
> My best friend is {easy-going} and never gets angry.
> Our neighbour is an {easy-going} man who rarely complains.
> I get on well with him because he is so relaxed and {easy-going}.
> Her {easy-going} personality makes her popular with everyone.
> My dad is pretty {easy-going} about what time I come home.
rebellious :: rebellisch
> Many teenagers go through a {rebellious} phase.
> As a teenager, he was {rebellious} and broke many of his parents' rules.
> Her {rebellious} behaviour often got her into trouble at school.
> The song is about a {rebellious} girl who refuses to follow orders.
> My little brother has become quite {rebellious} and argues about every rule.

## 3 Writing a comment – key words
statement :: Aussage
> The {statement} claims that our origin decides who we are.
> Do you agree with the following {statement}?
> In your introduction, you should refer to the {statement}.
> The minister made a short {statement} to the press.
> I think this {statement} is only partly true.
claim / to claim :: Behauptung / behaupten :: claim | to claim | claim / to claim
> The author {claims} that young people only care about likes. @ behaupten
> There is no proof for his {claim} that he saw a wolf. @ Behauptung
> Some people {claim} that video games make players violent. @ behaupten
> The advert makes the {claim} that this drink gives you more energy. @ Behauptung
> She {claimed} that she had never seen the message. @ behaupten (Vergangenheit)
argument :: Argument
> My strongest {argument} comes at the end.
> That is a convincing {argument}.
> You should give an example for each {argument}.
> The writer presents three {arguments} against school uniforms.
> His main {argument} is that homework causes too much stress.
counterargument :: Gegenargument :: counterargument | counter-argument
> A good comment takes up at least one {counterargument|counter-argument}.
> First she explained her own view, and then she dealt with a possible {counterargument|counter-argument}.
> A common {counterargument|counter-argument} is that uniforms are too expensive.
> He had no answer to my {counterargument|counter-argument}.
> If you mention a {counterargument|counter-argument}, you should try to refute it.
evidence :: Beleg, Beweis :: evidence
> You need {evidence|proof} to support your opinion.
> There is no scientific {evidence|proof} for this theory.
> The police are still looking for {evidence|proof}.
> The study provides clear {evidence|proof} that sleep helps us to learn.
> A claim without any {evidence|proof} is not very convincing.
to support :: stützen, untermauern :: support | to support
> {Support} every argument with an example.
> The figures in the table {support} my argument.
> Can you {support} your claim with facts?
> The author uses statistics to {support} her point of view.
> This example clearly {supports} the idea that friends influence us.
to refute :: widerlegen :: refute | to refute
> I can {refute} this argument with a simple example.
> The scientists were able to {refute} the old theory.
> It is difficult to {refute} such clear evidence.
> In the next paragraph, the writer tries to {refute} the counterargument.
> New research {refutes} the claim that we only use ten per cent of our brains.
point of view :: Standpunkt
> From my {point of view|viewpoint}, the statement is too simple.
> I understand your {point of view|viewpoint}, but I see things differently.
> Try to see the problem from your parents' {point of view|viewpoint}.
> The story is told from the {point of view|viewpoint} of a young girl.
> The two articles present different {points of view|viewpoints} on the topic.
to (dis)agree with :: (nicht) zustimmen :: agree with | to agree with | disagree with | to disagree with | to (dis)agree with
> I partly {agree with} the statement. @ zustimmen
> I completely {agree with} you – that is exactly what I think. @ zustimmen
> I {disagree with} the author because, in my view, his main argument is wrong. @ nicht zustimmen
> I am afraid I have to {disagree with} you; I see it quite differently. @ nicht zustimmen
> Most of my friends {agree with} me, so we are all on the same side. @ zustimmen
to be convinced (that) :: überzeugt sein (dass) :: to be convinced | be convinced | convinced | to be convinced that | be convinced that
> I am {convinced} that people can change.
> She is {convinced} that her team will win.
> We are {convinced} that this is the right decision.
> He was {convinced} that he had locked the door, but it was open.
> Are you really {convinced} that this plan will work?
conclusion :: Schluss(folgerung) :: conclusion
> Do not add new arguments in your {conclusion}.
> In your {conclusion}, you should state your opinion clearly.
> After looking at all the facts, I came to the {conclusion} that he was right.
> The essay has an introduction, a main part and a {conclusion}.
> It is too early to draw a {conclusion} from these results.

## 4 Phrases for your comment
In my opinion, … :: Meiner Meinung nach … :: in my opinion
> {In my opinion|From my point of view}, friends are just as important as family.
> {In my opinion|From my point of view}, school should start later in the morning.
> {In my opinion|From my point of view}, this is the best film of the year.
> {In my opinion|From my point of view}, nobody should be judged by their looks.
> {In my opinion|From my point of view}, learning languages is really useful.
I am convinced that … :: Ich bin überzeugt, dass … :: I am convinced that | I'm convinced that
> {I am convinced that|I'm convinced that} identity is not fixed.
> {I am convinced that|I'm convinced that} reading makes us more understanding.
> {I am convinced that|I'm convinced that} we can solve this problem together.
> {I am convinced that|I'm convinced that} every student has a special talent.
> {I am convinced that|I'm convinced that} honesty is always important in a friendship.
It is true that …, but … :: Es stimmt, dass …, aber … :: it is true that but | it is true that | it's true that but
> {It is true|It's true} that we cannot choose our parents, but we can choose our friends.
> {It is true|It's true} that social media can be useful, but it can also waste a lot of time.
> {It is true|It's true} that uniforms are practical, but many students do not like them.
> {It is true|It's true} that he made a mistake, but he has apologised.
> {It is true|It's true} that city life is exciting, but it can also be stressful.
Admittedly, … :: Zugegeben, … :: admittedly
> {Admittedly}, our hometown shapes us.
> {Admittedly}, I was not very polite to him.
> {Admittedly}, the plan has some weak points, but it is still worth trying.
> {Admittedly}, learning vocabulary is not always fun.
> {Admittedly}, this argument sounds convincing at first.
There is no doubt that … :: Es besteht kein Zweifel, dass … :: there is no doubt that | there's no doubt that
> {There is no doubt that|There's no doubt that} language is part of who we are.
> {There is no doubt that|There's no doubt that} smoking is bad for your health.
> {There is no doubt that|There's no doubt that} she is a talented singer.
> {There is no doubt that|There's no doubt that} the internet has changed our lives.
> {There is no doubt that|There's no doubt that} children need love and support.
This shows that … :: Das zeigt, dass … :: this shows that
> {This shows that} people can change.
> Many volunteers came to help. {This shows that} people care about their town.
> He kept trying until he succeeded. {This shows that} he never gives up.
> Even close friends sometimes disagree. {This shows that} friendship does not mean having the same opinion about everything.
> The number of members has doubled in one year. {This shows that} the club is becoming more popular.
Taking everything into account, … :: Alles in allem / Wenn man alles bedenkt, … :: taking everything into account
> {Taking everything into account}, the statement is too simple.
> {Taking everything into account}, I think the advantages are greater than the disadvantages.
> {Taking everything into account}, it was a very successful year.
> {Taking everything into account}, I would say that the author is only partly right.
> {Taking everything into account}, moving to the new school was a good decision.
That is why … :: Deshalb … :: that is why | that's why
> {That is why|That's why|Therefore} we should not judge people by their origin.
> I want to become a vet. {That is why|That's why|Therefore} I am doing work experience at an animal clinic.
> Exercise is good for your health. {That is why|That's why|Therefore} everyone should do some sport.
> My grandparents only speak Greek. {That is why|That's why|Therefore} I am learning the language.
> The roads were covered in ice. {That is why|That's why|Therefore} the school bus was late.

## 5 Linking words
first of all :: zuallererst
> {First of all|Firstly}, our family influences us.
> {First of all|Firstly}, I would like to thank you for your invitation.
> There are several reasons for this. {First of all|Firstly}, it saves money.
> {First of all|Firstly}, let us look at the advantages. After that, we will discuss the disadvantages.
> {First of all|Firstly}, I want to explain the rules of the game.
furthermore / moreover :: außerdem, darüber hinaus :: furthermore | moreover | furthermore / moreover
> {Furthermore|Moreover|In addition}, friends shape our interests.
> Cycling is cheap. {Furthermore|Moreover|In addition}, it is good for the environment.
> The flat is too small. {Moreover|Furthermore|In addition}, the rent is very high.
> The course is interesting. {Furthermore|Moreover|In addition}, the teacher explains everything clearly.
> Fast fashion creates a lot of waste. {Moreover|Furthermore|In addition}, many workers are badly paid.
in addition :: zusätzlich, außerdem :: in addition
> {In addition|Furthermore|Moreover}, school plays an important role.
> The hotel offers free breakfast. {In addition|Furthermore|Moreover}, guests can borrow bikes.
> She works as a nurse. {In addition|Furthermore|Moreover}, she coaches a children's football team.
> Reading improves your vocabulary. {In addition|Furthermore|Moreover}, it helps you to relax.
> You will need a passport. {In addition|Furthermore|Moreover}, you have to fill in this form.
for example / for instance :: zum Beispiel :: for example | for instance | for example / for instance
> {For example|For instance}, many teens copy their friends’ style.
> There are many ways to stay fit. You could, {for example|for instance}, go swimming.
> Some animals, {for example|for instance} bats, are active at night.
> You can help at home in many ways. {For example|For instance}, you can do the washing-up.
> Many English words come from other languages. “Piano”, {for example|for instance}, comes from Italian.
however :: jedoch :: however
> {However|Nevertheless}, not everybody wants to fit in.
> I wanted to go to the concert. {However}, all the tickets were sold out.
> The phone looks great. It is, {however}, far too expensive.
> Most people liked the idea. {However}, a few had some doubts.
> The weather forecast promised sunshine. {However}, it rained all day.
on the other hand :: andererseits :: on the other hand
> {On the other hand}, a hometown can feel too small.
> On the one hand, I would love to live abroad. {On the other hand}, I would miss my family.
> On the one hand, smartphones are useful. {On the other hand}, they can easily distract us.
> A part-time job gives you money of your own. {On the other hand}, it leaves you less time for studying.
> City life offers many opportunities. {On the other hand}, it can be noisy and expensive.
although :: obwohl :: although
> {Although|Though|Even though} he is shy, he performs on stage.
> {Although|Though|Even though} it was raining, we went for a walk.
> She passed the test {although|though|even though} she had not studied much.
> {Although|Though|Even though} they come from different countries, they are best friends.
> I still enjoyed the trip {although|though|even though} the journey was very long.
whereas :: wohingegen, während :: whereas
> My sister loves the city, {whereas|while|whilst} I prefer the countryside.
> Tom is very quiet, {whereas|while|whilst} his twin brother never stops talking.
> In the UK people drive on the left, {whereas|while|whilst} in Germany they drive on the right.
> Some students learn best in the morning, {whereas|while|whilst} others prefer to study at night.
> My old school was tiny, {whereas|while|whilst} my new one has over a thousand pupils.
nevertheless :: trotzdem, dennoch :: nevertheless
> It was hard. {Nevertheless}, she did not give up.
> He was very tired. {Nevertheless}, he finished his homework.
> The task seemed impossible. {Nevertheless}, they decided to try.
> I know the risks. {Nevertheless}, I want to take part.
> The tickets were expensive. {Nevertheless}, the concert was sold out.
despite + noun :: trotz :: despite
> {Despite|In spite of} her fear, she spoke up.
> {Despite|In spite of} the bad weather, the match went ahead.
> He went to school {despite|in spite of} his cold.
> {Despite|In spite of} all our efforts, we lost the game.
> They are still close friends {despite|in spite of} their differences.
because of + noun :: wegen :: because of
> {Because of|Due to|Owing to} social media, trends spread very fast.
> The match was cancelled {because of|due to|owing to} the heavy snow.
> We arrived late {because of|due to|owing to} a traffic jam.
> She could not take part in the race {because of|due to|owing to} her injury.
> {Because of|Due to|Owing to} the noise, I could not concentrate.
therefore :: deshalb, daher :: therefore
> {Therefore|As a result}, the statement is only partly true.
> The evidence is weak. We cannot, {therefore}, accept this claim.
> He is under eighteen and is {therefore} not allowed to vote in this election.
> The museum is closed on Mondays. We will {therefore} visit it on Tuesday.
> All the rooms were booked. {Therefore|As a result}, we had to find another hotel.
as a result :: folglich, infolgedessen :: as a result
> {As a result|Therefore}, many young people feel under pressure.
> He did not set his alarm. {As a result|Therefore}, he missed the bus.
> It did not rain for months. {As a result|Therefore}, many plants died.
> She practised every day. {As a result|Therefore}, her English improved a lot.
> The factory was shut down. {As a result|Therefore}, hundreds of people lost their jobs.
all in all / to sum up :: alles in allem / zusammenfassend :: all in all | to sum up | all in all / to sum up
> {All in all|To sum up}, we decide who we want to be.
> {All in all|To sum up}, I believe that the advantages are more important than the disadvantages.
> {All in all|To sum up}, it was a wonderful holiday.
> {To sum up|All in all}, both family and friends help to make us who we are.
> {All in all|To sum up}, the project was a great success.
"""

# Weitere richtige Antworten bei Deutsch → Englisch (gleiche deutsche Bedeutung)
EXTRA_ANSWERS = {
    "furthermore / moreover": ["in addition"],
    "in addition": ["furthermore", "moreover"],
    "therefore": ["that is why", "that's why"],
    "That is why …": ["therefore"],
    "to belong (to)": ["fit in", "to fit in"],
    "nevertheless": [],
}


def load_data():
    items, cat = [], "Allgemein"
    for line in RAW_DATA.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("## "):
            cat = line[3:].strip()
        elif line.startswith("> "):
            text, _, de_hint = line[2:].partition(" @ ")
            match = re.search(r"\{(.+?)\}", text)
            items[-1]["sentences"].append({
                "gap": text[:match.start()] + "_____" + text[match.end():],
                "answers": match.group(1).split("|"),
                "hint": de_hint.strip() or items[-1]["german"],
            })
        elif " :: " in line:
            parts = [p.strip() for p in line.split(" :: ")]
            en, de = parts[0], parts[1]
            accepted = [a.strip() for a in parts[2].split("|")] if len(parts) > 2 else [en]
            items.append({"id": en, "english": en, "german": de, "cat": cat,
                          "accepted": accepted, "sentences": []})
    return items


DATA = load_data()
CATEGORIES = list(dict.fromkeys(i["cat"] for i in DATA))
DE_TO_EN = {}
for _it in DATA:
    DE_TO_EN.setdefault(_it["german"], []).append(_it["english"])

# ----------------------------------------------------------------------------
# ANTWORT-AUSWERTUNG
# ----------------------------------------------------------------------------


def norm(s):
    s = s.lower().replace("ß", "ss").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    s = s.replace("…", " ")
    s = re.sub(r"[\u2010-\u2015\-]", " ", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def compact(s):
    return norm(s).replace(" ", "")


def answer_variants(text):
    """Zerlegt eine Bedeutung in akzeptierte Teilantworten.
    full    = vollständig gültige Antworten (getrennt durch ; / | oder :)
    partial = nur ein Teil einer Aufzählung mit ' – ' (zählt als 'teilweise')"""
    raw = text.strip()
    full = {raw}
    for p in re.split(r"\s*[;/|]\s*", raw):
        if p.strip():
            full.add(p.strip())
    if ":" in raw:
        for p in raw.split(":"):
            if p.strip():
                full.add(p.strip())
    if "…" not in raw:
        for v in list(full):
            full.update(p.strip() for p in v.split(",") if p.strip())
    for v in list(full):
        v2 = re.sub(r"\([^)]*\)", "", v)
        v2 = re.sub(r"\s+", " ", v2).strip()
        if v2:
            full.add(v2)
    partial = set()
    for v in list(full):
        parts = re.split(r"\s+[–—-]\s+", v)
        if len(parts) > 1:
            for p in parts:
                if p.strip():
                    partial.add(p.strip())
    return full, partial - full


def evaluate(user, expected, tol=0.88):
    """Rückgabe: 'empty' | 'correct' | 'almost' | 'partial' | 'wrong'"""
    u = compact(user)
    if not u:
        return "empty"
    full, partial = answer_variants(expected)
    best = 0.0
    for c in full:
        cc = compact(c)
        if not cc:
            continue
        if u == cc:
            return "correct"
        best = max(best, SequenceMatcher(None, u, cc).ratio())
    for c in partial:
        if u == compact(c):
            return "partial"
    thr = tol if len(u) > 5 else max(tol, 0.92)
    if best >= 0.96:
        return "correct"
    if best >= thr:
        return "almost"
    return "wrong"


def evaluate_english(user, answers, tol=0.88):
    """Englisch wird streng geprüft: Schon eine falsche Endung (z. B. fehlendes -s)
    zählt nicht als richtig, sondern höchstens als 'fast richtig'."""
    u = norm(user)
    if not u:
        return "empty"
    targets = [norm(a) for a in answers]
    if u in targets:
        return "correct"
    if max(SequenceMatcher(None, u, t).ratio() for t in targets) >= tol:
        return "almost"
    return "wrong"


def hint_text(text, level):
    first = re.split(r"\s*[;/|]\s*", text)[0]
    first = re.sub(r"\([^)]*\)", "", first)
    out = []
    for tok in first.split():
        if not any(ch.isalpha() for ch in tok):
            out.append(tok)
            continue
        shown, res = 0, ""
        for ch in tok:
            if ch.isalpha():
                res += ch if shown < level else "_"
                shown += 1
            else:
                res += ch
        out.append(res)
    return " ".join(out)



# ----------------------------------------------------------------------------
# KONSTANTEN & EINSTELLUNGEN
# ----------------------------------------------------------------------------
BOX_DAYS = {1: 0, 2: 1, 3: 3, 4: 7, 5: 21}
CLOZE_TYPE, CLOZE_MC = "Lückensatz (Eintippen)", "Lückensatz (Auswahl)"
MODES = ["Eintippen", "Multiple Choice", "Karteikarten", CLOZE_TYPE, CLOZE_MC]
CLOZE_MODES = (CLOZE_TYPE, CLOZE_MC)
TYPED_MODES = ("Eintippen", CLOZE_TYPE)
CHOICE_MODES = ("Multiple Choice", CLOZE_MC)
# Wörter mit ähnlicher Funktion stehen bei der Satz-Auswahl nie gemeinsam zur Wahl
SIMILAR = [
    {"furthermore / moreover", "in addition", "first of all", "for example / for instance"},
    {"therefore", "as a result", "That is why …", "This shows that …", "because of + noun"},
    {"however", "nevertheless", "on the other hand", "although", "whereas", "despite + noun",
     "Admittedly, …", "It is true that …, but …"},
    {"In my opinion, …", "point of view", "I am convinced that …", "to be convinced (that)",
     "There is no doubt that …", "Taking everything into account, …", "all in all / to sum up"},
    {"statement", "claim / to claim", "argument", "counterargument", "evidence", "conclusion"},
    {"to belong (to)", "to fit in", "to identify with sb./sth."},
    {"background", "roots (pl.)", "heritage", "upbringing", "culture", "tradition", "identity"},
    {"stereotype", "prejudice"},
]
DIRECTIONS = ["Englisch → Deutsch", "Deutsch → Englisch", "Gemischt"]
STRATEGIES = ["Intelligent (fällige zuerst)", "Zufällig", "Reihenfolge des Vokabelblatts",
              "Nur neue Vokabeln", "Nur schwierige", "Nur Favoriten"]
COUNTS = ["10", "20", "30", "50", "Alle"]
STATUS_FILTER = ["Alle", "Neu", "Schwierig", "Favoriten", "Gelernt (Box 4–5)", "Fällig"]

DEFAULT_SETTINGS = {
    "tolerance": 0.88, "auto_next": True, "auto_delay": 1100,
    "timer": False, "timer_seconds": 20, "auto_hint": False, "q_size": 30,
    "mode": "Eintippen", "direction": "Englisch → Deutsch", "strategy": STRATEGIES[0],
    "count": "20", "cats": None,
}
BY_ID = {i["id"]: i for i in DATA}


def _stretch(fn):
    try:
        return {"width": "stretch"} if "width" in inspect.signature(fn).parameters else {"use_container_width": True}
    except (TypeError, ValueError):
        return {}


W_BTN = _stretch(st.button)
W_FSB = _stretch(st.form_submit_button)
W_DF = _stretch(st.dataframe)
W_DL = _stretch(st.download_button)


# ----------------------------------------------------------------------------
# SPEICHER
# ----------------------------------------------------------------------------
def load_store():
    try:
        return json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def init_state():
    if "store" in st.session_state:
        return
    raw = load_store()
    settings = dict(DEFAULT_SETTINGS)
    settings.update(raw.get("settings", {}))
    st.session_state.store = {
        "cards": raw.get("cards", {}), "favorites": set(raw.get("favorites", [])),
        "sent": raw.get("sent", {}), "daily": raw.get("daily", {}), "best_streak": raw.get("best_streak", 0), "settings": settings,
    }
    st.session_state.view = "setup"
    st.session_state.sess = None


def store():
    return st.session_state.store


def cfg():
    return st.session_state.store["settings"]


def ss():
    return st.session_state.sess


def export_dict():
    S = store()
    return {"cards": S["cards"], "favorites": sorted(S["favorites"]), "daily": S["daily"],
            "sent": S["sent"],
            "best_streak": S["best_streak"], "settings": S["settings"]}


def save():
    try:
        tmp = SAVE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(export_dict(), ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(SAVE_FILE)
    except OSError:
        pass


def toast(msg):
    st.session_state.flash_msg = msg


# ----------------------------------------------------------------------------
# KARTEIKASTEN (LEITNER)
# ----------------------------------------------------------------------------
def box_of(cid):
    c = store()["cards"].get(cid)
    return c["box"] if c else 0


def record_result(cid, ok):
    now = time.time()
    cards = store()["cards"]
    c = cards.get(cid)
    if c is None:
        c = cards[cid] = {"box": 1, "due": now, "ok": 0, "bad": 0, "streak": 0, "last": now}
    if ok:
        c["ok"] += 1
        c["streak"] += 1
        c["box"] = min(5, c["box"] + 1)
    else:
        c["bad"] += 1
        c["streak"] = 0
        c["box"] = 1
    c["last"] = now
    c["due"] = now + BOX_DAYS[c["box"]] * 86400
    d = store()["daily"].setdefault(date.today().isoformat(), {"asked": 0, "ok": 0})
    d["asked"] += 1
    d["ok"] += 1 if ok else 0
    save()


def undo_record(cid, prev):
    cards = store()["cards"]
    if prev is None:
        cards.pop(cid, None)
    else:
        cards[cid] = prev
    d = store()["daily"].get(date.today().isoformat())
    if d:
        d["asked"] = max(0, d["asked"] - 1)


def cat_stats():
    now = time.time()
    res = {c: {"n": 0, "new": 0, "due": 0, "mastered": 0} for c in CATEGORIES}
    cards = store()["cards"]
    for it in DATA:
        r = res[it["cat"]]
        r["n"] += 1
        c = cards.get(it["id"])
        if c is None:
            r["new"] += 1
        else:
            r["due"] += c["due"] <= now
            r["mastered"] += c["box"] >= 4
    return res


def day_streak():
    daily = store()["daily"]
    d, n = date.today(), 0
    if daily.get(d.isoformat(), {}).get("asked", 0) == 0:
        d -= timedelta(days=1)
    while daily.get(d.isoformat(), {}).get("asked", 0) > 0:
        n += 1
        d -= timedelta(days=1)
    return n


# ----------------------------------------------------------------------------
# SITZUNG
# ----------------------------------------------------------------------------
def build_queue(pool, strategy, n):
    now = time.time()
    cards, favs = store()["cards"], store()["favorites"]
    if strategy.startswith("Intelligent"):
        due = [i for i in pool if i["id"] in cards and cards[i["id"]]["due"] <= now]
        due.sort(key=lambda i: (cards[i["id"]]["box"], random.random()))
        new = [i for i in pool if i["id"] not in cards]
        random.shuffle(new)
        rest = sorted((i for i in pool if i["id"] in cards and cards[i["id"]]["due"] > now),
                      key=lambda i: cards[i["id"]]["due"])
        q = due + new + rest
    elif strategy.startswith("Reihenfolge"):
        q = list(pool)
    elif strategy.startswith("Nur neue"):
        q = [i for i in pool if i["id"] not in cards]
    elif strategy.startswith("Nur schwierige"):
        q = [i for i in pool if i["id"] in cards and cards[i["id"]]["bad"] > 0]
        q.sort(key=lambda i: -(cards[i["id"]]["bad"] - cards[i["id"]]["ok"]))
    elif strategy.startswith("Nur Favoriten"):
        q = [i for i in pool if i["id"] in favs]
    else:
        q = list(pool)
        random.shuffle(q)
    if n:
        q = q[:n]
    if not strategy.startswith("Reihenfolge"):
        random.shuffle(q)
    return q


def collect_setup():
    c, g = cfg(), st.session_state.get
    c["mode"] = g("s_mode", c["mode"])
    c["direction"] = g("s_dir", c["direction"])
    c["strategy"] = g("s_strategy", c["strategy"])
    c["count"] = g("s_count", c["count"])
    if any(f"cat_{i}" in st.session_state for i in range(len(CATEGORIES))):
        c["cats"] = [cat for i, cat in enumerate(CATEGORIES) if g(f"cat_{i}", True)]
    save()


def start_session(ids=None):
    collect_setup()
    c = cfg()
    if ids is None:
        cats = c["cats"] if c["cats"] is not None else CATEGORIES
        if not cats:
            toast("Bitte mindestens ein Kapitel auswählen.")
            return
        pool = [i for i in DATA if i["cat"] in cats]
        n = None if c["count"] == "Alle" else int(c["count"])
        ids = [i["id"] for i in build_queue(pool, c["strategy"], n)]
    if not ids:
        toast("Für diese Auswahl gibt es keine passenden Vokabeln. Wähle eine andere Auswahl oder andere Kapitel.")
        return
    st.session_state.sess = dict(
        queue=list(ids), total=len(ids), done=0, correct_first=0, wrong_first=0, streak=0, best=0,
        attempted=set(), sent=None, repeats={}, wrong_items=[], start=time.time(), mode=c["mode"], dirsel=c["direction"],
        current=None, direction="la", awaiting=False, revealed=False, hint_level=0, last_info=None,
        fb="", fb_kind="", n=0, mc_options=[], mc_correct="", mc_pick=None, deadline=0.0,
        allow_override=False, auto_pending=False)
    st.session_state.view = "card"
    next_card()


def quick_due():
    now = time.time()
    cards = store()["cards"]
    due = [i for i in DATA if i["id"] in cards and cards[i["id"]]["due"] <= now]
    if not due:
        toast("Aktuell ist nichts fällig 🎉 Starte eine Sitzung mit neuen Vokabeln.")
        return
    due.sort(key=lambda i: (cards[i["id"]]["box"], random.random()))
    start_session([i["id"] for i in due[:30]])


def repeat_wrong():
    ids = list(ss().get("wrong_items", []))
    if ids:
        random.shuffle(ids)
        start_session(ids)


def back_to_setup():
    st.session_state.view = "setup"


def set_all_cats(val):
    for i in range(len(CATEGORIES)):
        st.session_state[f"cat_{i}"] = val


def cats_with_due():
    st_ = cat_stats()
    for i, cat in enumerate(CATEGORIES):
        st.session_state[f"cat_{i}"] = st_[cat]["due"] > 0


def expected_raw():
    """Nur für deutsche Antworten (Englisch → Deutsch)."""
    return BY_ID[ss()["current"]]["german"]


def english_answers():
    """Alle richtigen englischen Antworten für die aktuelle Aufgabe."""
    s = ss()
    if s["mode"] in CLOZE_MODES:
        return s["sent"]["answers"]
    it = BY_ID[s["current"]]
    out = []
    for en in DE_TO_EN[it["german"]]:
        out += BY_ID[en]["accepted"] + EXTRA_ANSWERS.get(en, [])
    return out


def full_sentence(sent):
    return sent["gap"].replace("_____", sent["answers"][0])


def expected_display():
    s = ss()
    if s["mode"] in CLOZE_MODES:
        it, sent = BY_ID[s["current"]], s["sent"]
        text = f"Lösung: {sent['answers'][0]}"
        if len(sent["answers"]) > 1:
            text += f"  (auch richtig: {', '.join(sent['answers'][1:])})"
        return f"{text}\n{full_sentence(sent)}\n{it['english']} = {it['german']}"
    it = BY_ID[s["current"]]
    if s["direction"] == "la":
        return it["german"]
    return "   oder   ".join(DE_TO_EN[it["german"]])


def pick_sentence(cid):
    """Wählt zufällig einen Satz; erst wenn alle dran waren, wiederholt sich einer."""
    sentences = BY_ID[cid]["sentences"]
    seen = store()["sent"].get(cid, [])
    free = [i for i in range(len(sentences)) if i not in seen]
    if not free:
        free = [i for i in range(len(sentences)) if i != (seen[-1] if seen else None)]
        seen = []
    idx = random.choice(free)
    store()["sent"][cid] = seen + [idx]
    return sentences[idx]


def build_mc():
    s = ss()
    it, to_de = BY_ID[s["current"]], s["direction"] == "la"
    cloze = s["mode"] in CLOZE_MODES

    def ans(x):
        if cloze:
            return x["english"]
        return x["german"] if to_de else "   oder   ".join(DE_TO_EN[x["german"]])

    correct = ans(it)
    blocked = set()
    if cloze:
        for group in SIMILAR:
            if it["id"] in group:
                blocked |= group
    pool = [x for x in DATA if x["german"] != it["german"] and x["id"] not in blocked]
    same = [x for x in pool if x["cat"] == it["cat"]]
    other = [x for x in pool if x["cat"] != it["cat"]]
    random.shuffle(same)
    random.shuffle(other)
    wrong = []
    for x in same + other:
        a = ans(x)
        if a != correct and a not in wrong:
            wrong.append(a)
        if len(wrong) == 3:
            break
    opts = wrong + [correct]
    random.shuffle(opts)
    s["mc_options"], s["mc_correct"], s["mc_pick"] = opts, correct, None


def next_card():
    s = ss()
    if not s["queue"]:
        finish_session()
        return
    cid = s["queue"].pop(0)
    s["current"] = cid
    d = s["dirsel"]
    # "la" = Antwort auf Deutsch, "de" = Antwort auf Englisch
    s["direction"] = "la" if d.startswith("Englisch") else "de" if d.startswith("Deutsch") else random.choice(("la", "de"))
    if s["mode"] in CLOZE_MODES:
        s["direction"] = "de"
        s["sent"] = pick_sentence(cid)
    s.update(awaiting=False, revealed=False, hint_level=0, last_info=None, fb="", fb_kind="",
             n=s["n"] + 1, allow_override=False, auto_pending=False)
    if s["mode"] in CHOICE_MODES:
        build_mc()
    if s["mode"] in TYPED_MODES and cfg()["auto_hint"]:
        s["hint_level"] = 1
    if cfg()["timer"] and s["mode"] != "Karteikarten":
        s["deadline"] = time.time() + int(cfg()["timer_seconds"])


def finish_session():
    s = ss()
    if not s:
        st.session_state.view = "setup"
        return
    s["awaiting"] = True
    st.session_state.view = "summary"
    save()


def hint():
    s = ss()
    if s and s["mode"] in TYPED_MODES and not s["awaiting"]:
        s["hint_level"] += 1


def check_answer():
    s = ss()
    if s["awaiting"]:
        return
    ans = st.session_state.get(f"ans_{s['n']}", "")
    if s["direction"] == "la":
        st_ = evaluate(ans, expected_raw(), cfg()["tolerance"])
    else:
        st_ = evaluate_english(ans, english_answers(), cfg()["tolerance"])
        if s["mode"] == CLOZE_TYPE and st_ in ("almost", "wrong"):
            base = {norm(a) for a in BY_ID[s["current"]]["accepted"]}
            if norm(ans) in base:
                st_ = "form"
    if st_ == "empty":
        s["fb"], s["fb_kind"] = "Bitte zuerst eine Antwort eingeben – oder „Weiß ich nicht“ wählen.", "info"
    elif st_ == "correct":
        grade(True, "✓ Richtig!")
    elif st_ == "form":
        grade(False, "≈ Richtiges Wort, aber die Form passt nicht in den Satz")
    elif st_ == "almost":
        grade(False, "≈ Fast richtig – kleiner Fehler", allow_override=True)
    elif st_ == "partial":
        grade(False, "≈ Nur ein Teil – es fehlt noch etwas", allow_override=True)
    else:
        grade(False, "✗ Leider falsch")


def give_up():
    if not ss()["awaiting"]:
        grade(False, "Aufgedeckt")


def grade(ok, headline, allow_override=False):
    s = ss()
    if s["awaiting"] or s["current"] is None:
        return
    s["awaiting"] = True
    cid = s["current"]
    first = cid not in s["attempted"]
    s["attempted"].add(cid)
    prev = copy.deepcopy(store()["cards"].get(cid)) if first else None
    if first:
        record_result(cid, ok)
        if ok:
            s["correct_first"] += 1
        else:
            s["wrong_first"] += 1
            s["wrong_items"].append(cid)
    requeued = done_inc = False
    if ok:
        s["streak"] += 1
        s["best"] = max(s["best"], s["streak"])
        store()["best_streak"] = max(store()["best_streak"], s["streak"])
        s["done"] += 1
        done_inc = True
    else:
        s["streak"] = 0
        r = s["repeats"].get(cid, 0)
        if r < 2:
            s["repeats"][cid] = r + 1
            s["queue"].insert(min(len(s["queue"]), 3), cid)
            requeued = True
        else:
            s["done"] += 1
            done_inc = True
    s["last_info"] = dict(cid=cid, first=first, prev=prev, requeued=requeued, done_inc=done_inc, ok=ok)
    text = headline + ("\n" + expected_display() if headline else expected_display())
    user = st.session_state.get(f"ans_{s['n']}", "").strip() if s["mode"] in TYPED_MODES else ""
    if not ok and user and headline != "Aufgedeckt":
        text += f"\n(deine Antwort: {user})"
    s["fb"] = text
    s["fb_kind"] = "good" if ok else "warn" if allow_override else "bad"
    s["allow_override"] = allow_override
    s["auto_pending"] = bool(ok and cfg()["auto_next"] and s["mode"] != "Karteikarten")
    save()


def override():
    s = ss()
    info = s["last_info"]
    if not s["awaiting"] or not info or info["ok"]:
        return
    cid = info["cid"]
    if info["first"]:
        undo_record(cid, info["prev"])
        record_result(cid, True)
        s["wrong_first"] -= 1
        s["correct_first"] += 1
        if cid in s["wrong_items"]:
            s["wrong_items"].remove(cid)
    if info["requeued"]:
        if cid in s["queue"]:
            s["queue"].remove(cid)
        s["repeats"][cid] -= 1
    if not info["done_inc"]:
        s["done"] += 1
    s["streak"] += 1
    s["best"] = max(s["best"], s["streak"])
    info["ok"] = True
    s["allow_override"] = False
    s["fb"], s["fb_kind"] = "✓ Als richtig gewertet\n" + expected_display(), "good"
    save()


def choose(i):
    s = ss()
    if s["awaiting"] or i >= len(s["mc_options"]):
        return
    s["mc_pick"] = i
    ok = s["mc_options"][i] == s["mc_correct"]
    grade(ok, "✓ Richtig!" if ok else "✗ Leider falsch")


def flip():
    s = ss()
    if s["revealed"] or s["awaiting"]:
        return
    s["revealed"] = True
    s["fb"], s["fb_kind"] = expected_display(), "accent"


def flash_answer(ok):
    s = ss()
    if not s["revealed"] or s["awaiting"]:
        return
    s["fb"], s["fb_kind"] = "", ""
    grade(ok, "")
    next_card()


def toggle_fav(cid):
    favs = store()["favorites"]
    favs ^= {cid}
    save()


# ----------------------------------------------------------------------------
# OBERFLÄCHE
# ----------------------------------------------------------------------------
def md_escape(text):
    for ch in ("\\", "*", "_", "`", "~", "<", ">", "#", "$"):
        text = text.replace(ch, "\\" + ch)
    return text.replace("\n", "  \n")


def centered(text, size="1rem", color=None, weight="400", mono=False, opacity=None):
    style = f"text-align:center;font-size:{size};font-weight:{weight};"
    if color:
        style += f"color:{color};"
    if opacity:
        style += f"opacity:{opacity};"
    if mono:
        style += "font-family:monospace;"
    st.markdown(f"<div style='{style}'>{html.escape(text)}</div>", unsafe_allow_html=True)


def show_feedback(s):
    if not s["fb"]:
        return
    kind = s["fb_kind"]
    if kind == "accent":
        centered(s["fb"], "1.7rem", "#6c8cff", "700")
        return
    {"good": st.success, "warn": st.warning, "bad": st.error, "info": st.info}.get(kind, st.info)(md_escape(s["fb"]))


def _timer_body():
    s = ss()
    if not s or s["awaiting"] or st.session_state.view != "card":
        return
    rem = int(s["deadline"] - time.time()) + 1
    if rem <= 0:
        grade(False, "⏱ Zeit abgelaufen")
        st.rerun()
    else:
        st.caption(f"⏱ {rem} s")


_timer_fragment = st.fragment(run_every=1)(_timer_body) if hasattr(st, "fragment") else None


def render_setup():
    c = cfg()
    cs = cat_stats()
    tot = {k: sum(v[k] for v in cs.values()) for k in ("n", "new", "due", "mastered")}
    st.caption(f"{tot['n']} Vokabeln  •  {tot['mastered']} gelernt  •  {tot['due']} fällig  •  {tot['new']} neu")
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("Kapitel auswählen")
            for i, cat in enumerate(CATEGORIES):
                r = cs[cat]
                st.checkbox(f"{cat}   ({r['n']} • {r['due']} fällig • {r['new']} neu)",
                            value=(c["cats"] is None or cat in c["cats"]), key=f"cat_{i}")
            b1, b2, b3 = st.columns(3)
            b1.button("Alle", on_click=set_all_cats, args=(True,), **W_BTN)
            b2.button("Keine", on_click=set_all_cats, args=(False,), **W_BTN)
            b3.button("Nur mit fälligen", on_click=cats_with_due, **W_BTN)
    with right:
        with st.container(border=True):
            st.subheader("Lernsitzung")

            def pick(label, opts, key, cur):
                st.selectbox(label, opts, index=opts.index(cur) if cur in opts else 0, key=key)

            pick("Modus", MODES, "s_mode", c["mode"])
            pick("Richtung", DIRECTIONS, "s_dir", c["direction"])
            pick("Auswahl", STRATEGIES, "s_strategy", c["strategy"])
            pick("Anzahl Vokabeln", COUNTS, "s_count", c["count"])
            st.button("▶  Lernen starten", type="primary", on_click=start_session, **W_BTN)
            st.button("⏰  Nur fällige Vokabeln wiederholen", on_click=quick_due, **W_BTN)
            st.caption("Tipp: Richtig beantwortete Vokabeln wandern im Karteikasten eine Box höher und kommen "
                       "später wieder (1 → 3 → 7 → 21 Tage). Falsche starten wieder in Box 1.")


def render_card():
    s, c = ss(), cfg()
    cid = s["current"]
    it = BY_ID[cid]
    mode, n, la = s["mode"], s["n"], s["direction"] == "la"
    b = box_of(cid)

    a, m, r = st.columns([2, 3, 2])
    a.markdown("🆕 **Neue Vokabel**" if b == 0 else f"📦 **Box {b} von 5**")
    m.caption(it["cat"])
    r.caption(f"{s['done']} / {s['total']} geschafft  •  {len(s['queue']) + 1} offen")
    st.progress(min(1.0, s["done"] / max(1, s["total"])))

    with st.container(border=True):
        cloze = mode in CLOZE_MODES
        if cloze:
            centered("Welche englische Vokabel fehlt?", opacity="0.6")
            centered(s["sent"]["gap"], f"{int(c['q_size'])}px", weight="700")
            centered(f"Gesucht: {s['sent']['hint']}", "1.1rem", opacity="0.75")
        else:
            centered("Englisch → Deutsch" if la else "Deutsch → Englisch", opacity="0.6")
            centered(it["english"] if la else it["german"], f"{int(c['q_size'])}px", weight="700")
        if s["hint_level"] and not s["awaiting"]:
            solution = expected_raw() if la else (s["sent"]["answers"][0] if cloze else it["accepted"][0])
            centered("Hinweis:  " + hint_text(solution, s["hint_level"]), "1.3rem", "#ffb454", mono=True)

        if mode in TYPED_MODES:
            if not s["awaiting"]:
                with st.form(f"form_{n}", clear_on_submit=False):
                    st.text_input("Deine Antwort", key=f"ans_{n}", label_visibility="collapsed",
                                  placeholder="Fehlendes englisches Wort eintippen und Enter drücken …" if cloze
                                  else "Übersetzung eintippen und Enter drücken …")
                    f1, f2, f3 = st.columns(3)
                    f1.form_submit_button("Prüfen  ↵", type="primary", on_click=check_answer, **W_FSB)
                    f2.form_submit_button("💡 Hinweis", on_click=hint, **W_FSB)
                    f3.form_submit_button("Weiß ich nicht", on_click=give_up, **W_FSB)
        elif mode in CHOICE_MODES:
            if not s["awaiting"]:
                for i, o in enumerate(s["mc_options"]):
                    st.button(f"{i + 1}   {o}", key=f"mc_{n}_{i}", on_click=choose, args=(i,), **W_BTN)
            else:
                for i, o in enumerate(s["mc_options"]):
                    mark = "✅" if o == s["mc_correct"] else "❌" if i == s["mc_pick"] else "▫️"
                    st.markdown(f"{mark}  {md_escape(o)}")
        elif not s["revealed"]:
            centered("Überlege dir die Antwort – dann „Umdrehen“.", opacity="0.6")

        show_feedback(s)
        if c["timer"] and mode != "Karteikarten" and not s["awaiting"]:
            if _timer_fragment:
                _timer_fragment()

    # Aktionsleiste
    names = []
    if mode == "Karteikarten":
        names = ["flip"] if not s["revealed"] else ["know", "dont"]
    elif s["awaiting"]:
        if s["allow_override"] and not s["last_info"]["ok"]:
            names.append("override")
        names.append("next")
    elif mode in CHOICE_MODES:
        names.append("giveup")
    names += ["fav", "stop"]
    cols = st.columns(len(names))
    for col, name in zip(cols, names):
        with col:
            if name == "flip":
                st.button("Umdrehen", key=f"b_flip_{n}", type="primary", on_click=flip, **W_BTN)
            elif name == "know":
                st.button("✓ Gewusst", key=f"b_know_{n}", type="primary", on_click=flash_answer, args=(True,), **W_BTN)
            elif name == "dont":
                st.button("✗ Nicht gewusst", key=f"b_dont_{n}", on_click=flash_answer, args=(False,), **W_BTN)
            elif name == "override":
                st.button("✔ Als richtig werten", key=f"b_ov_{n}", on_click=override, **W_BTN)
            elif name == "next":
                st.button("Weiter  ↵", key=f"b_next_{n}", type="primary", on_click=next_card, **W_BTN)
            elif name == "giveup":
                st.button("Weiß ich nicht", key=f"b_gu_{n}", on_click=give_up, **W_BTN)
            elif name == "fav":
                st.button("★ Favorit" if cid in store()["favorites"] else "☆ Favorit", key=f"b_fav_{n}",
                          on_click=toggle_fav, args=(cid,), **W_BTN)
            else:
                st.button("Beenden", key=f"b_stop_{n}", on_click=finish_session, **W_BTN)

    if s.get("auto_pending"):
        time.sleep(int(c["auto_delay"]) / 1000)
        s["auto_pending"] = False
        next_card()
        st.rerun()


def render_summary():
    s = ss()
    first = s["correct_first"] + s["wrong_first"]
    pct = (s["correct_first"] / first * 100) if first else 0
    mins, secs = divmod(int(time.time() - s["start"]), 60)
    title = ("Sitzung beendet" if first == 0 else "🏆 Hervorragend!" if pct >= 90 else
             "👍 Gut gemacht!" if pct >= 70 else "💪 Dranbleiben – Übung macht den Meister!")
    with st.container(border=True):
        st.subheader(title)
        st.markdown(f"Beim ersten Versuch richtig: **{s['correct_first']} von {first}** ({pct:.0f} %)  \n"
                    f"Beste Serie: **{s['best']}**   •   Dauer: **{mins} min {secs:02d} s**")
        st.caption("Diese Vokabeln solltest du nochmal ansehen:")
        if s["wrong_items"]:
            st.dataframe(pd.DataFrame([{"Englisch": BY_ID[i]["english"], "Deutsch": BY_ID[i]["german"]}
                                       for i in s["wrong_items"]]), hide_index=True, **W_DF)
        else:
            st.success("Keine Fehler – stark! 🎉")
        b1, b2 = st.columns(2)
        b1.button("🔁 Fehler wiederholen", type="primary", on_click=repeat_wrong,
                  disabled=not s["wrong_items"], **W_BTN)
        b2.button("Neue Sitzung", on_click=back_to_setup, **W_BTN)


def render_learn():
    v = st.session_state.view
    if v == "card" and ss() and ss()["current"] is not None:
        render_card()
    elif v == "summary" and ss():
        render_summary()
    else:
        render_setup()


# --------------------------------------------------------------- Vokabelliste
def list_action(what, ids):
    S = store()
    now = time.time()
    for cid in ids:
        if what == "fav":
            S["favorites"] ^= {cid}
        elif what == "learned":
            c = S["cards"].setdefault(cid, {"box": 5, "due": now, "ok": 0, "bad": 0, "streak": 0, "last": now})
            c["box"], c["due"] = 5, now + BOX_DAYS[5] * 86400
        elif what == "reset":
            S["cards"].pop(cid, None)
    save()


def render_list():
    S = store()
    c1, c2, c3 = st.columns([2, 2, 1.5])
    q = norm(c1.text_input("Suche", key="list_q"))
    cat = c2.selectbox("Kapitel", ["Alle Kapitel"] + CATEGORIES, key="list_cat")
    stat = c3.selectbox("Status", STATUS_FILTER, key="list_stat")
    now = time.time()
    rows, ids = [], []
    for it in DATA:
        c = S["cards"].get(it["id"])
        is_new, due = c is None, (c is not None and c["due"] <= now)
        hard = bool(c and c["bad"] > c["ok"])
        if cat != "Alle Kapitel" and it["cat"] != cat:
            continue
        if q and q not in norm(it["english"]) and q not in norm(it["german"]):
            continue
        if stat == "Neu" and not is_new:
            continue
        if stat == "Schwierig" and not hard:
            continue
        if stat == "Favoriten" and it["id"] not in S["favorites"]:
            continue
        if stat.startswith("Gelernt") and not (c and c["box"] >= 4):
            continue
        if stat == "Fällig" and not due:
            continue
        status = "🆕 neu" if is_new else "✅ gelernt" if c["box"] >= 4 else "⚠️ schwierig" if hard else ""
        rows.append({"★": "★" if it["id"] in S["favorites"] else "", "Englisch": it["english"], "Deutsch": it["german"],
                     "Beispielsatz": full_sentence(it["sentences"][0]),
                     "Kapitel": it["cat"], "Box": "–" if is_new else str(c["box"]),
                     "✓/✗": "" if is_new else f'{c["ok"]}/{c["bad"]}', "Status": status})
        ids.append(it["id"])
    st.caption(f"{len(rows)} von {len(DATA)} Vokabeln  •  Zeilen anklicken zum Auswählen")
    sel_ids = []
    if rows:
        df = pd.DataFrame(rows)
        try:
            ev = st.dataframe(df, hide_index=True, height=480, on_select="rerun", selection_mode="multi-row",
                              key="list_df", **W_DF)
            sel_ids = [ids[i] for i in ev.selection.rows if i < len(ids)]
        except TypeError:
            st.dataframe(df, hide_index=True, height=480, **W_DF)
            st.info("Für die Auswahl von Zeilen bitte Streamlit aktualisieren (pip install -U streamlit).")
    b1, b2, b3, _ = st.columns([1.3, 1.6, 1.3, 2])
    b1.button("★ Favorit umschalten", on_click=list_action, args=("fav", sel_ids), disabled=not sel_ids, **W_BTN)
    b2.button("Als gelernt markieren (Box 5)", on_click=list_action, args=("learned", sel_ids),
              disabled=not sel_ids, **W_BTN)
    b3.button("Zurücksetzen (neu)", on_click=list_action, args=("reset", sel_ids), disabled=not sel_ids, **W_BTN)


# ------------------------------------------------------------------ Statistik
def render_stats():
    S = store()
    cards = S["cards"]
    now = time.time()
    ok = sum(c["ok"] for c in cards.values())
    bad = sum(c["bad"] for c in cards.values())
    mastered = sum(c["box"] >= 4 for c in cards.values())
    due = sum(c["due"] <= now for c in cards.values())
    seen = len(cards)
    acc = (ok / (ok + bad) * 100) if ok + bad else 0

    m = st.columns(6)
    m[0].metric("Vokabeln gesamt", len(DATA))
    m[1].metric("Schon gesehen", seen)
    m[2].metric("Gelernt (Box 4–5)", mastered)
    m[3].metric("Jetzt fällig", due)
    m[4].metric("Trefferquote", f"{acc:.0f} %")
    m[5].metric("Lerntage in Folge", day_streak())
    st.caption(f"Antworten gesamt: {ok + bad}   •   Beste Serie richtig: {S['best_streak']}   •   "
               f"Favoriten: {len(S['favorites'])}")

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("Karteikasten")
            counts = {b: 0 for b in range(6)}
            counts[0] = len(DATA) - seen
            for c in cards.values():
                counts[c["box"]] += 1
            for b in range(6):
                a, p, n_ = st.columns([1, 6, 1])
                a.write("Neu" if b == 0 else f"Box {b}")
                p.progress(counts[b] / max(1, len(DATA)))
                n_.write(str(counts[b]))
        with st.container(border=True):
            st.subheader("Letzte 7 Tage")
            days = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]
            vals = [S["daily"].get(d.isoformat(), {"asked": 0, "ok": 0}) for d in days]
            df = pd.DataFrame({"Richtig": [v["ok"] for v in vals],
                               "Falsch": [v["asked"] - v["ok"] for v in vals]},
                              index=[d.strftime("%d.%m.") for d in days])
            st.bar_chart(df, color=["#34c88a", "#ff6b6b"])
    with right:
        with st.container(border=True):
            st.subheader("Fortschritt je Kapitel")
            st.caption("Gelernt = Box 4–5")
            for cat, r in cat_stats().items():
                a, p, n_ = st.columns([4, 3, 1])
                a.write(cat)
                p.progress(r["mastered"] / max(1, r["n"]))
                n_.write(f"{r['mastered']}/{r['n']}")
        with st.container(border=True):
            st.subheader("Die schwierigsten Vokabeln")
            hard = sorted((it for it in DATA if it["id"] in cards and cards[it["id"]]["bad"] > 0),
                          key=lambda it: -cards[it["id"]]["bad"])[:6]
            if hard:
                st.dataframe(pd.DataFrame([{"Englisch": it["english"], "Deutsch": it["german"],
                                            "✗": cards[it["id"]]["bad"]} for it in hard]),
                             hide_index=True, **W_DF)
            else:
                st.caption("Noch keine Fehler – weiter so!")


# ------------------------------------------------------------- Einstellungen
def on_setting():
    c, g = cfg(), st.session_state.get
    c["q_size"] = int(g("set_q", c["q_size"]))
    c["tolerance"] = float(g("set_tol", c["tolerance"]))
    c["auto_hint"] = bool(g("set_hint", c["auto_hint"]))
    c["auto_next"] = bool(g("set_next", c["auto_next"]))
    c["timer"] = bool(g("set_timer", c["timer"]))
    c["timer_seconds"] = int(g("set_tsec", c["timer_seconds"]))
    c["auto_delay"] = int(g("set_delay", c["auto_delay"]))
    save()


def import_progress():
    f = st.session_state.get("imp_file")
    if not f:
        return
    try:
        d = json.loads(f.getvalue().decode("utf-8"))
        S = store()
        S["cards"], S["favorites"] = d.get("cards", {}), set(d.get("favorites", []))
        S["daily"], S["best_streak"] = d.get("daily", {}), d.get("best_streak", 0)
        S["sent"] = d.get("sent", {})
        save()
        toast("Fortschritt importiert ✅")
    except Exception:
        toast("Die Datei konnte nicht gelesen werden.")


def reset_all():
    S = store()
    S["cards"], S["daily"], S["best_streak"], S["favorites"] = {}, {}, 0, set()
    S["sent"] = {}
    st.session_state.reset_ok = False
    save()
    toast("Fortschritt zurückgesetzt.")


def render_settings():
    c = cfg()
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.subheader("Darstellung")
            st.caption("Hell/Dunkel: oben rechts ⋮ → Settings → Theme.")
            st.number_input("Schriftgröße der Frage", 18, 50, int(c["q_size"]), key="set_q", on_change=on_setting)
            st.slider("Tippfehler-Toleranz (höher = strenger)", 0.80, 0.98, float(c["tolerance"]), 0.01,
                      key="set_tol", on_change=on_setting)
    with right:
        with st.container(border=True):
            st.subheader("Lernhilfen")
            st.checkbox("Anfangsbuchstaben automatisch anzeigen", value=c["auto_hint"], key="set_hint", on_change=on_setting)
            st.checkbox("Nach richtiger Antwort automatisch weiter", value=c["auto_next"], key="set_next", on_change=on_setting)
            st.checkbox("Zeitlimit pro Vokabel", value=c["timer"], key="set_timer", on_change=on_setting)
            st.number_input("Zeitlimit (Sekunden)", 5, 120, int(c["timer_seconds"]), key="set_tsec", on_change=on_setting)
            st.number_input("Pause nach richtiger Antwort (ms)", 300, 5000, int(c["auto_delay"]), 100,
                            key="set_delay", on_change=on_setting)
    with st.container(border=True):
        st.subheader("Daten")
        S = store()
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button("⬇ Fortschritt sichern (JSON)", json.dumps(export_dict(), ensure_ascii=False, indent=1),
                               file_name="englisch_fortschritt.json", mime="application/json", **W_DL)
            hard = [it for it in DATA if it["id"] in S["cards"] and S["cards"][it["id"]]["bad"] > S["cards"][it["id"]]["ok"]]
            if hard:
                st.download_button("⬇ Schwierige Vokabeln (TXT)", "\n".join(f'{i["english"]}  –  {i["german"]}' for i in hard),
                                   file_name="schwierige_vokabeln.txt", **W_DL)
            else:
                st.caption("Es gibt noch keine schwierigen Vokabeln.")
        with d2:
            st.file_uploader("Fortschritt importieren", type=["json"], key="imp_file")
            st.button("Importieren", on_click=import_progress, disabled=not st.session_state.get("imp_file"), **W_BTN)
        with d3:
            st.checkbox("Ja, wirklich alles löschen", key="reset_ok")
            st.button("Gesamten Fortschritt zurücksetzen", type="primary", on_click=reset_all,
                      disabled=not st.session_state.get("reset_ok"), **W_BTN)
        st.caption("Hinweis: Auf Streamlit Cloud geht die gespeicherte Datei bei einem Neustart verloren – "
                   "sichere deinen Fortschritt dort regelmäßig über den Export.")


# ----------------------------------------------------------------------------
# HAUPTPROGRAMM
# ----------------------------------------------------------------------------
def main():
    init_state()
    msg = st.session_state.pop("flash_msg", None)
    if msg:
        st.toast(msg)
    S = store()
    d = S["daily"].get(date.today().isoformat(), {"asked": 0, "ok": 0})
    s = ss()
    streak = s["streak"] if (s and st.session_state.view == "card") else 0
    h1, h2 = st.columns([2, 3])
    h1.title("🇬🇧 English Vocabulary Trainer")
    h2.markdown(f"<div style='text-align:right;padding-top:1.4rem'>🔥 Serie: {streak} &nbsp;&nbsp; Heute: "
               f"{d['ok']} / {d['asked']} richtig &nbsp;&nbsp; Lerntage in Folge: {day_streak()}</div>",
               unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["Lernen", "Vokabelliste", "Statistik", "Einstellungen"])
    with t1:
        render_learn()
    with t2:
        render_list()
    with t3:
        render_stats()
    with t4:
        render_settings()


main()