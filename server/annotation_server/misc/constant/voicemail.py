#!/usr/bin/python3
# -*- coding: utf-8 -*-


class AnnotateMode(object):
    increase = 'increase'
    correction = 'correction'


class RecommendMode(object):
    random = 'random'

    voicemail = 'voicemail'
    mute = 'mute'
    white_noise = 'white_noise'
    bell = 'bell'
    noise = 'noise'
    voice = 'voice'
    noise_mute = 'noise_mute'
    other = 'other'
    music = 'music'

    @classmethod
    def all(cls):
        return [
            cls.random,
            cls.voicemail,
            cls.mute,
            cls.white_noise,
            cls.bell,
            cls.noise,
            cls.voice,
            cls.noise_mute,
            cls.other,
            cls.music,
        ]


class ChoiceOfLabel(object):
    voicemail = 'voicemail'
    non_voicemail = 'non_voicemail'
    mute = 'mute'
    white_noise = 'white_noise'
    bell = 'bell'
    noise = 'noise'
    voice = 'voice'
    noise_mute = 'noise_mute'
    other = 'other'
    music = 'music'

    @classmethod
    def all(cls):
        return [
            cls.voicemail,
            # cls.non_voicemail,
            cls.mute,
            cls.white_noise,
            cls.bell,
            cls.noise,
            cls.voice,
            cls.noise_mute,
            cls.other,
            cls.music,
        ]


if __name__ == '__main__':
    pass
