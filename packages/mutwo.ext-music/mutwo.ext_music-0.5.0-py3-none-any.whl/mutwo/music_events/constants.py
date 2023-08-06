"""Set default values for :class:`mutwo.ext.events.music.NoteLike`."""

from mutwo import music_parameters

DEFAULT_PLAYING_INDICATORS_COLLECTION_CLASS = (
    music_parameters.playing_indicators.PlayingIndicatorCollection
)
"""Default value for :attr:`~mutwo.ext.events.music.NoteLike.playing_indicator_collection`
in :class:`~mutwo.ext.events.music.NoteLike`"""

DEFAULT_NOTATION_INDICATORS_COLLECTION_CLASS = (
    music_parameters.notation_indicators.NotationIndicatorCollection
)
"""Default value for :attr:`~mutwo.ext.events.music.NoteLike.notation_indicator_collection`
in :class:`~mutwo.ext.events.music.NoteLike`"""
