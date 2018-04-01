from django.shortcuts import render
from django.utils import timezone
from .models import Post
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator
from watson_developer_cloud import PersonalityInsightsV3


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='02b20e7e-5854-404e-8f77-11990c5e5759',
        password='MnocvW2pDKv1',
        version='2016-05-19')
#Language Translator Inputs
    language_translator = LanguageTranslator(
        username='95c4eb96-7340-4c84-b421-ca6733aed7a3',
        password='XdvhvNWVuSZX')
#PErsonality Judgement
    personality_insights = PersonalityInsightsV3(
        version='2017-10-13',
        username='4a271c79-410e-4745-ba73-fd7c014686b9',
        password='mfFCtQk3JnYN')


    for post in posts:
        posting = post.text
        toneObj= json.dumps(tone_analyzer.tone(tone_input=posting,
                                   content_type="text/plain"), indent=2)
        post.toneObj2 = json.loads(toneObj)
        # print(post.toneObj2)
        post.angerScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][0]['score']
        post.disgustScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][1]['score']
        post.fearScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][2]['score']
        post.joyScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][3]['score']
        post.sadScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][4]['score']

#Personality Insights -
        profileObj = json.dumps(personality_insights.profile(content=posting,
                                                             content_type="text/plain",
                                                             raw_scores=True,
                                                             consumption_preferences=True),indent=2)
        post.profileObj2 = json.loads(profileObj)

        post.personalityKind = post.profileObj2['personality'][1]['name']
        # post.personalityScore = post.profileObj2['personality'][2]
        post.percentile = post.profileObj2['personality'][3]['percentile']
        post.percentileValue = post.percentile*100
        post.personalityTrait = post.profileObj2['personality'][4]['raw_score']
        print(post.personalityKind)
        print(post.personalityTrait)

      #Language Translation API
        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='es')
        obj= json.dumps(translation, indent=2, ensure_ascii=False)
        post.language_translation_object = json.loads(obj)
        post.translations = post.language_translation_object['translations']
        post.trns_key = post.translations[0]
        post.translation_spanish = post.trns_key['translation']
        post.word_count = post.language_translation_object['word_count']
        post.character_count = post.language_translation_object['character_count']


    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})