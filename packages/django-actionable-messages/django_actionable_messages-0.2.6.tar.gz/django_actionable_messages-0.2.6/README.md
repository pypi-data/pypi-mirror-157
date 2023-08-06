<h1 align="center">
    <a href="https://github.com/utsurius/django-actionable-messages">
        Actionable messages
    </a>
</h1>

<p align="center">
    <a href="https://github.com/utsurius/django-actionable-messages/releases">
        <img src="https://img.shields.io/github/release/utsurius/django-actionable-messages" alt="github"/>
    </a>
    <a href="https://pypi.python.org/pypi/django-actionable-messages">
        <img src="https://badge.fury.io/py/django-actionable-messages.svg" alt="pypi"/>
    </a>
    <a href="https://github.com/utsurius/django-actionable-messages">
        <img src="https://img.shields.io/pypi/pyversions/django_actionable_messages.svg" alt="python"/>
    </a>
    <a href="https://github.com/utsurius/django-actionable-messages">
        <img src="https://img.shields.io/pypi/djversions/django_actionable_messages.svg" alt="django"/>
    </a>
    <a href="https://github.com/utsurius/django-actionable-messages/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/utsurius/django-actionable-messages" alt="license"/>
    </a>
</p>

1. [Base informations](#base-informations)
2. [Installation](#installation)
3. [Requirements](#requirements)
4. [Usage](#usage)
5. [AdaptiveCard](#adaptivecard)
    * [Elements](#adaptivecard-elements)
        * [TextBlock](#adaptivecard-textblock)
        * [Image](#adaptivecard-image)
        * [MediaSource](#adaptivecard-mediasource)
        * [Media](#adaptivecard-media)
        * [TextRun](#adaptivecard-textrun)
        * [RichTextBlock](#adaptivecard-richtextblock)
    * [Inputs](#adaptivecard-inputs)
        * [TextInput](#adaptivecard-textinput)
        * [NumberInput](#adaptivecard-numberinput)
        * [DateInput](#adaptivecard-dateinput)
        * [TimeInput](#adaptivecard-timeinput)
        * [ToggleInput](#adaptivecard-toggleinput)
        * [InputChoice](#adaptivecard-inputchoice)
        * [ChoiceSetInput](#adaptivecard-choicesetinput)
    * [Actions](#adaptivecard-actions)
        * [OpenUrl](#adaptivecard-openurl)
        * [Submit](#adaptivecard-submit)
        * [ShowCard](#adaptivecard-showcard)
        * [TargetElement](#adaptivecard-targetelement)
        * [ToggleVisibility](#adaptivecard-togglevisibility)
        * [Execute](#adaptivecard-execute)
    * [Containers](#adaptivecard-containers)
        * [ActionSet](#adaptivecard-actionset)
        * [Container](#adaptivecard-container)
        * [Column](#adaptivecard-column)
        * [ColumnSet](#adaptivecard-columnset)
        * [Fact](#adaptivecard-fact)
        * [FactSet](#adaptivecard-factset)
        * [ImageSet](#adaptivecard-imageset)
        * [TableCell](#adaptivecard-tablecell)
        * [TableRow](#adaptivecard-tablerow)
        * [Table](#adaptivecard-table)
    * [Types](#adaptivecard-types)
        * [BackgroundImage](#adaptivecard-backgroundimage)
        * [Refresh](#adaptivecard-refresh)
        * [TokenExchangeResource](#adaptivecard-tokenexchangeresource)
        * [AuthCardButton](#adaptivecard-authcardbutton)
        * [Authentication](#adaptivecard-authentication)
    * [Cards](#adaptivecard-cards)
        * [AdaptiveCard](#adaptivecard-adaptivecard)
6. [MessageCard](#messagecard)
    * [Elements](#messagecard-elements)
        * [Header](#messagecard-header)
        * [Fact](#messagecard-fact)
        * [HeroImage](#messagecard-heroimage)
        * [InputChoice](#messagecard-inputchoice)
        * [ActionTarget](#messagecard-actiontarget)
    * [Inputs](#messagecard-inputs)
        * [TextInput](#messagecard-textinput)
        * [DateInput](#messagecard-dateinput)
        * [MultiChoiceInput](#messagecard-multichoiceinput)
    * [Actions](#messagecard-actions)
        * [OpenUri](#messagecard-openuri)
        * [HttpPOST](#messagecard-httppost)
        * [InvokeAddInCommand](#messagecard-invokeaddincommand)
        * [ActionCard](#messagecard-actioncard)
    * [Sections](#messagecard-sections)
        * [Section](#messagecard-section)
    * [Cards](#messagecard-cards)
        * [MessageCard](#messagecard-messagecard)
7. [HeroCard](#herocard)
    * [Elements](#herocard-elements)
        * [OpenUrl](#herocard-openurl)
        * [Image](#herocard-image)
    * [Cards](#herocard-cards)
        * [HeroCard](#herocard-herocard)
8. [ThumbnailCard](#thumbnailcard)
    * [Elements](#thumbnailcard-elements)
    * [Cards](#thumbnailcard-cards)
        * [ThumbnailCard](#thumbnailcard-thumbnailcard)


<h2 id="base-informations">Base informations</h2>

[Playground V2](https://messagecardplayground.azurewebsites.net/)

[Send an actionable message via email in Office 365](https://docs.microsoft.com/en-gb/outlook/actionable-messages/send-via-email)

[Outlook version requirements for actionable messages](https://docs.microsoft.com/en-us/outlook/actionable-messages/#outlook-version-requirements-for-actionable-messages)


<h2 id="installation">Installation</h2>

`pip install git+https://github.com/utsurius/django-actionable-messages`

`pip install django-actionable-messages`

Add "django_actionable_messages" to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    "django_actionable_messages",
]
```

SETTINGS

```python
ACTIONABLE_MESSAGES = {
    "JSON_ENCODER": None,
    "LANGUAGE_CODE": "en"
}
```

"JSON_ENCODER" - doted path to custom json encoder (default: BaseEncoder).

"LANGUAGE_CODE" - language code used for translations (defaults to project settings.LANGUAGE_CODE). Each element of adaptive_card/message_card can set individual "lang_code".


<h2 id="requirements">Requirements</h2>

| Name    | Version    |
|---------|------------|
| python  | 3.5 - 3.10 |
| django  | 2.2 - 4.0  |


<h2 id="usage">Usage</h2>

**`examples/message_card/github.py`**

```python
from django_actionable_messages.message_card.actions import OpenUri, HttpPOST, ActionCard
from django_actionable_messages.message_card.cards import MessageCard
from django_actionable_messages.message_card.elements import Fact, ActionTarget
from django_actionable_messages.message_card.inputs import TextInput
from django_actionable_messages.message_card.sections import Section
from django_actionable_messages.message_card.utils import OSType


issue_opened = MessageCard(title="Issue opened: \"Push notifications not working\"", summary="Issue 176715375",
                           theme_color="0078D7")
issue_opened.add_sections(
    Section(
        activity_title="Miguel Garcie",
        activity_subtitle="9/13/2016, 11:46am",
        activity_image="https://connectorsdemo.azurewebsites.net/images/MSC12_Oscar_002.jpg",
        text="There is a problem with Push notifications, they don't seem to be picked up by the connector.",
        facts=[
            Fact("Repository:", "mgarcia\\test"),
            Fact("Issue #:", "176715375")
        ]
    )
)
issue_opened.add_actions([
    ActionCard(
        name="Add a comment",
        inputs=[
            TextInput(input_id="comment", title="Enter a comment", is_multiline=True)
        ],
        actions=[
            HttpPOST("OK", target="http://...")
        ]
    ),
    HttpPOST("Close", target="http://..."),
    OpenUri(name="View in Github", targets=[
        ActionTarget(OSType.DEFAULT, "http://...")
    ])
])
```

**`examples/adaptive_card/calendar_reminder.py`**

```python
from django_actionable_messages.adaptive_card.actions import Submit
from django_actionable_messages.adaptive_card.cards import AdaptiveCard
from django_actionable_messages.adaptive_card.elements import TextBlock
from django_actionable_messages.adaptive_card.inputs import InputChoice, ChoiceSetInput
from django_actionable_messages.adaptive_card.utils import SCHEMA, FontSize, FontWeight, SpacingStyle, ChoiceInputStyle


calendar_reminder = AdaptiveCard(version="1.0", schema=SCHEMA)
calendar_reminder.set_speak("Your  meeting about \"Adaptive Card design session\" is starting at 12:30pm"
                            "Do you want to snooze  or do you want to send a late notification to the attendees?")
calendar_reminder.add_elements(TextBlock("Adaptive Card design session", size=FontSize.LARGE, weight=FontWeight.BOLDER))
calendar_reminder.add_elements([
    TextBlock("Conf Room 112/3377 (10)", is_subtle=True),
    TextBlock("12:30 PM - 1:30 PM", is_subtle=True, spacing=SpacingStyle.NONE),
    TextBlock("Snooze for")
])
calendar_reminder.add_elements(ChoiceSetInput(
    item_id="snooze", style=ChoiceInputStyle.COMPACT, value="5", choices=[
        InputChoice("5 minutes", "5"),
        InputChoice("15 minutes", "15"),
        InputChoice("30 minutes", "30")
    ]
))
calendar_reminder.add_actions([
    Submit(title="Snooze", data={
        "x": "snooze"
    }),
    Submit(title="I'll be late", data={
        "x": "late"
    })
])
```

For more view **`examples`** folder

To get dictionary, json or html payload from card use:

| Property             | Type                                                                                                                                                      |
|----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| .payload             | *dict* (raw data)                                                                                                                                         |
| .json_payload        | json string                                                                                                                                               |
| .html_payload        | html string - can be used to send card via email ([docs](https://docs.microsoft.com/en-gb/outlook/actionable-messages/send-via-email))                    |
| .signed_html_payload | html string<sup>1</sup> - can be used to send card via email ([docs](https://docs.microsoft.com/en-us/outlook/actionable-messages/security-requirements)) |

\[1\] you must overwrite **get_signed_payload()** in AdaptiveCard/MessageCard to sign the payload!


Problem: **'... is not JSON serializable'** - probably invalid argument type was used. Default json serializer can handle translated strings and everything that `DjangoJSONEncoder` can handle. 

Solution: [Better Python Object Serialization](https://hynek.me/articles/serialization/). Remember to ALWAYS inherit from EncoderMixin or BaseEncoder (`django_actionable_messages.encoders import EncoderMixin, BaseEncoder`)

You can set JSON_ENCODER (globally) in SETTINGS(ACTIONABLE_MESSAGES) or set it by card(json_encoder):

```python
from django_actionable_messages.adaptive_card.cards import AdaptiveCard


class MyAdaptiveCard(AdaptiveCard):
    json_encoder = "path.to.my.encoder"
```
or
```python
from django_actionable_messages.adaptive_card.cards import AdaptiveCard


class MyAdaptiveCard(AdaptiveCard):
    json_encoder = MyJSONEncoder
```

To customize json dump you can overwrite `get_json_dump_kwargs()` in card (AdaptiveCard/MessageCard)

```python
from django_actionable_messages.adaptive_card.cards import AdaptiveCard


class MyAdaptiveCard(AdaptiveCard):
    def get_json_dump_kwargs(self):
        return {
            'ensure_ascii': False,
            'indent': 2
        }
```

Send MessageCard to msteams using webhooks and `requests` library:
```python
import requests


requests.post(
    webhook_url,
    data=card.json_payload,
    headers={
        "Content-Type": "application/json; charset=utf-8"
    }
)
``` 

To get/add `webhook_url` see here: [Get the Microsoft Teams webhook URL](https://learning.getpostman.com/docs/postman_pro/integrations/microsoft_teams/#get-the-microsoft-teams-webhook-url), [Create and add an outgoing webhook in Teams](https://support.office.com/en-ie/article/create-and-add-an-outgoing-webhook-in-teams-8e1a1648-982f-4511-b342-6d8492437207)

<h2 id="adaptivecard">AdaptiveCard</h2>

Supported versions: **1.0 - 1.5**

[Schema Explorer](https://adaptivecards.io/explorer/)


<h3 id="adaptivecard-elements">Elements</h3>

**src**: `from django_actionable_messages.adaptive_card.elements import ...`

<h4 id="adaptivecard-textblock">TextBlock <a href="https://adaptivecards.io/explorer/TextBlock.html">docs</a></h4>

| Argument name        | Function                   | Property            | Type                                                   |
|----------------------|----------------------------|---------------------|--------------------------------------------------------|
| **text**             | set_text()                 | text                | *str, trans<sup>3</sup>*                               |
| color                | set_color()                | color               | Color<sup>1</sup>                                      |
| font_type            | set_font_type()            | fontType            | FontType<sup>1</sup>                                   |
| horizontal_alignment | set_horizontal_alignment() | horizontalAlignment | HorizontalAlignment<sup>1</sup>                        |
| is_subtle            | set_is_subtle()            | isSubtle            | *bool*                                                 |
| max_lines            | set_max_lines()            | maxLines            | *int*                                                  |
| size                 | set_size()                 | size                | FontSize<sup>1</sup>                                   |
| weight               | set_weight()               | weight              | FontWeight<sup>1</sup>                                 |
| wrap                 | set_wrap()                 | wrap                | *bool*                                                 |
| fallback             | set_fallback()             | fallback            | FallbackOption<sup>1</sup> or card element<sup>2</sup> |
| separator            | set_separator()            | separator           | *bool*                                                 |
| spacing              | set_spacing()              | spacing             | SpacingStyle<sup>1</sup>                               |
| item_id              | set_id()                   | id                  | *str*                                                  |
| is_visible           | set_is_visible()           | isVisible           | *bool*                                                 |
| requires             | set_requires()             | requires            | *dict*                                                 |
| height               | set_height()               | height              | BlockElementHeight<sup>1</sup>                         |
| lang_code            | -                          | -                   | *str*                                                  |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[2\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

\[3\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="adaptivecard-image">Image <a href="https://adaptivecards.io/explorer/Image.html">docs</a></h4>

| Argument name        | Function                   | Property            | Type                                                   |
|----------------------|----------------------------|---------------------|--------------------------------------------------------|
| **url**              | set_url()                  | url                 | *str*                                                  |
| alternate_text       | set_alternate_text()       | altText             | *str*                                                  |
| background_color     | set_background_color()     | backgroundColor     | *str*                                                  |
| height               | set_height()               | height              | str or BlockElementHeight<sup>1</sup>                  |
| horizontal_alignment | set_horizontal_alignment() | horizontalAlignment | HorizontalAlignment<sup>1</sup>                        |
| select_action        | set_select_action()        | selectAction        | see docs                                               |
| size                 | set_size()                 | size                | ImageSize<sup>1</sup>                                  |
| style                | set_style()                | style               | ImageStyle<sup>1</sup>                                 |
| width                | set_width()                | width               | *str*                                                  |
| fallback             | set_fallback()             | fallback            | FallbackOption<sup>1</sup> or card element<sup>2</sup> |
| separator            | set_separator()            | separator           | *bool*                                                 |
| spacing              | set_spacing()              | spacing             | SpacingStyle<sup>1</sup>                               |
| item_id              | set_id()                   | id                  | *str*                                                  |
| is_visible           | set_is_visible()           | isVisible           | *bool*                                                 |
| requires             | set_requires()             | requires            | *dict*                                                 |
| height               | set_height()               | height              | BlockElementHeight<sup>1</sup>                         |
| lang_code            | -                          | -                   | *str*                                                  |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[2\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

<h4 id="adaptivecard-mediasource">MediaSource <a href="https://adaptivecards.io/explorer/MediaSource.html">docs</a></h4>

| Argument name | Property | Type   |
|---------------|----------|--------|
| **mime_type** | mimeType | *str*  |
| **url**       | url      | *str*  |

<h4 id="adaptivecard-media">Media <a href="https://adaptivecards.io/explorer/Media.html">docs</a></h4>

| Argument name  | Function             | Property  | Type                                                   |
|----------------|----------------------|-----------|--------------------------------------------------------|
| **sources**    | add_sources()        | sources   | *list* of MediaSource(s)<sup>1</sup>                   |
| poster         | set_poster()         | poster    | *str*                                                  |
| alternate_text | set_alternate_text() | altText   | *str*                                                  |
| fallback       | set_fallback()       | fallback  | FallbackOption<sup>2</sup> or card element<sup>1</sup> |
| separator      | set_separator()      | separator | *bool*                                                 |
| spacing        | set_spacing()        | spacing   | SpacingStyle<sup>2</sup>                               |
| item_id        | set_id()             | id        | *str*                                                  |
| is_visible     | set_is_visible()     | isVisible | *bool*                                                 |
| requires       | set_requires()       | requires  | *dict*                                                 |
| height         | set_height()         | height    | BlockElementHeight<sup>2</sup>                         |
| lang_code      | -                    | -         | *str*                                                  |

Other functions

| Name          | Property | Type                     |
|---------------|----------|--------------------------|
| add_source()  | sources  | MediaSource<sup>1</sup>  |

\[1\] `from django_actionable_messages.adaptive_cards.elements import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

<h4 id="adaptivecard-textrun">TextRun <a href="https://adaptivecards.io/explorer/TextRun.html">docs</a></h4>

| Argument name  | Function             | Property      | Type                      |
|----------------|----------------------|---------------|---------------------------|
| **text**       | set_text()           | text          | *str*, trans <sup>2</sup> |
| color          | set_color()          | color         | Color<sup>1</sup>         |
| font_type      | set_font_type()      | fontType      | FontType<sup>1</sup>      |
| highlight      | set_highlight()      | highlight     | *bool*                    |
| is_subtle      | set_is_subtle()      | isSubtle      | *bool*                    |
| italic         | set_italic()         | italic        | *bool*                    |
| select_action  | set_select_action()  | selectAction  | see docs                  |
| size           | set_size()           | fontSize      | FontSize<sup>1</sup>      |
| strike_through | set_strike_through() | strikethrough | *bool*                    |
| weight         | set_weight()         | fontWeight    | FontWeight<sup>1</sup>    |
| lang_code      | -                    | -             | *str*                     |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[2\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="adaptivecard-richtextblock">RichTextBlock <a href="https://adaptivecards.io/explorer/RichTextBlock.html">docs</a></h4>

| Argument name        | Function                   | Property            | Type                                                   |
|----------------------|----------------------------|---------------------|--------------------------------------------------------|
| **inlines**          | set_inlines()              | inlines             | *str*, TextRun<sup>1</sup>, trans<sup>4</sup>          |
| horizontal_alignment | set_horizontal_alignment() | horizontalAlignment | HorizontalAlignment<sup>2</sup>                        |
| fallback             | set_fallback()             | fallback            | FallbackOption<sup>2</sup> or card element<sup>1</sup> |
| separator            | set_separator()            | separator           | *bool*                                                 |
| spacing              | set_spacing()              | spacing             | SpacingStyle<sup>2</sup>                               |
| item_id              | set_id()                   | id                  | *str*                                                  |
| is_visible           | set_is_visible()           | isVisible           | *bool*                                                 |
| requires             | set_requires()             | requires            | *dict*                                                 |
| height               | set_height()               | height              | BlockElementHeight<sup>2</sup>                         |

\[1\] `from django_actionable_messages.adaptive_cards.elements import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

\[4\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h3 id="adaptivecard-inputs">Inputs</h3>

**src**: `from django_actionable_messages.adaptive_card.inputs import ...`

<h4 id="adaptivecard-textinput">TextInput <a href="https://adaptivecards.io/explorer/Input.Text.html">docs</a></h4>

| Argument name | Function            | Property     | Type                                                    |
|---------------|---------------------|--------------|---------------------------------------------------------|
| is_multiline  | set_is_multiline()  | isMultiline  | *bool*                                                  |
| max_length    | set_max_length()    | maxLength    | *int*                                                   |
| placeholder   | set_placeholder()   | placeholder  | *str*, trans<sup>3</sup>                                |
| style         | set_style()         | style        | TextInputStyle<sup>1</sup>                              |
| inline_action | set_inline_action() | inlineAction | see docs                                                |
| value         | set_value()         | value        | *str*, trans<sup>3</sup>                                |
| fallback      | set_fallback()      | fallback     | FallbackOption<sup>1</sup> or card element<sup>2</sup>  |
| separator     | set_separator()     | separator    | *bool*                                                  |
| spacing       | set_spacing()       | spacing      | SpacingStyle<sup>1</sup>                                |
| item_id       | set_id()            | id           | *str*                                                   |
| is_visible    | set_is_visible()    | isVisible    | *bool*                                                  |
| requires      | set_requires()      | requires     | *dict*                                                  |
| height        | set_height()        | height       | BlockElementHeight<sup>1</sup>                          |
| label         | set_label()         | label        | *str*, TextBlock<sup>4</sup>, RichTextBlock<sup>4</sup> |
| lang_code     | -                   | -            | *str*                                                   |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[2\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

\[3\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

\[4\] `from django_actionable_messages.adaptive_cards.elements import ...`

<h4 id="adaptivecard-numberinput">NumberInput <a href="https://adaptivecards.io/explorer/Input.Number.html">docs</a></h4>

| Argument name | Function          | Property    | Type                                                    |
|---------------|-------------------|-------------|---------------------------------------------------------|
| max_value     | set_max_value()   | maxValue    | *int*                                                   |
| min_value     | set_min_value()   | minValue    | *int*                                                   |
| placeholder   | set_placeholder() | placeholder | *str*, trans<sup>3</sup>                                |
| value         | set_value()       | value       | *int*                                                   |
| fallback      | set_fallback()    | fallback    | FallbackOption<sup>1</sup> or card element<sup>2</sup>  |
| separator     | set_separator()   | separator   | *bool*                                                  |
| spacing       | set_spacing()     | spacing     | SpacingStyle<sup>1</sup>                                |
| item_id       | set_id()          | id          | *str*                                                   |
| is_visible    | set_is_visible()  | isVisible   | *bool*                                                  |
| requires      | set_requires()    | requires    | *dict*                                                  |
| height        | set_height()      | height      | BlockElementHeight<sup>1</sup>                          |
| label         | set_label()       | label       | *str*, TextBlock<sup>4</sup>, RichTextBlock<sup>4</sup> |
| lang_code     | -                 | -           | *str*                                                   |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[2\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

\[3\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

\[4\] `from django_actionable_messages.adaptive_cards.elements import ...`

<h4 id="adaptivecard-dateinput">DateInput <a href="https://adaptivecards.io/explorer/Input.Date.html">docs</a></h4>

| Argument name | Function          | Property    | Type                                                    |
|---------------|-------------------|-------------|---------------------------------------------------------|
| max_value     | set_max_value()   | maxValue    | *str*                                                   |
| min_value     | set_min_value()   | minValue    | *str*                                                   |
| placeholder   | set_placeholder() | placeholder | *str*, trans<sup>3</sup>                                |
| value         | set_value()       | value       | *str*                                                   |
| fallback      | set_fallback()    | fallback    | FallbackOption<sup>1</sup> or card element<sup>2</sup>  |
| separator     | set_separator()   | separator   | *bool*                                                  |
| spacing       | set_spacing()     | spacing     | SpacingStyle<sup>1</sup>                                |
| item_id       | set_id()          | id          | *str*                                                   |
| is_visible    | set_is_visible()  | isVisible   | *bool*                                                  |
| requires      | set_requires()    | requires    | *dict*                                                  |
| height        | set_height()      | height      | BlockElementHeight<sup>1</sup>                          |
| label         | set_label()       | label       | *str*, TextBlock<sup>4</sup>, RichTextBlock<sup>4</sup> |
| lang_code     | -                 | -           | *str*                                                   |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[2\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

\[3\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

\[4\] `from django_actionable_messages.adaptive_cards.elements import ...`

<h4 id="adaptivecard-timeinput">TimeInput <a href="https://adaptivecards.io/explorer/Input.Time.html">docs</a></h4>

| Argument name | Function          | Property    | Type                                                    |
|---------------|-------------------|-------------|---------------------------------------------------------|
| max_value     | set_max_value()   | maxValue    | *str*                                                   |
| min_value     | set_min_value()   | minValue    | *str*                                                   |
| placeholder   | set_placeholder() | placeholder | *str*, trans<sup>3</sup>                                |
| value         | set_value()       | value       | *str*                                                   |
| fallback      | set_fallback()    | fallback    | FallbackOption<sup>1</sup> or card element<sup>2</sup>  |
| separator     | set_separator()   | separator   | *bool*                                                  |
| spacing       | set_spacing()     | spacing     | SpacingStyle<sup>1</sup>                                |
| item_id       | set_id()          | id          | *str*                                                   |
| is_visible    | set_is_visible()  | isVisible   | *bool*                                                  |
| requires      | set_requires()    | requires    | *dict*                                                  |
| height        | set_height()      | height      | BlockElementHeight<sup>1</sup>                          |
| label         | set_label()       | label       | *str*, TextBlock<sup>4</sup>, RichTextBlock<sup>4</sup> |
| lang_code     | -                 | -           | *str*                                                   |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[2\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

\[3\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

\[4\] `from django_actionable_messages.adaptive_cards.elements import ...`

<h4 id="adaptivecard-toggleinput">ToggleInput <a href="https://adaptivecards.io/explorer/Input.Toggle.html">docs</a></h4>

| Argument name | Function         | Property  | Type                                                    |
|---------------|------------------|-----------|---------------------------------------------------------|
| **title**     | set_title()      | title     | *str*, trans<sup>3</sup>                                |
| value         | set_value()      | value     | *str*                                                   |
| value_off     | set_value_off()  | valueOff  | *str*                                                   |
| value_on      | set_value_on()   | valueOn   | *str*                                                   |
| wrap          | set_wrap()       | wrap      | *bool*                                                  |
| fallback      | set_fallback()   | fallback  | FallbackOption<sup>1</sup> or card element<sup>2</sup>  |
| separator     | set_separator()  | separator | *bool*                                                  |
| spacing       | set_spacing()    | spacing   | SpacingStyle<sup>1</sup>                                |
| item_id       | set_id()         | id        | *str*                                                   |
| is_visible    | set_is_visible() | isVisible | *bool*                                                  |
| requires      | set_requires()   | requires  | *dict*                                                  |
| height        | set_height()     | height    | BlockElementHeight<sup>1</sup>                          |
| label         | set_label()      | label     | *str*, TextBlock<sup>4</sup>, RichTextBlock<sup>4</sup> |
| lang_code     | -                | -         | *str*                                                   |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[2\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

\[3\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

\[4\] `from django_actionable_messages.adaptive_cards.elements import ...`

<h4 id="adaptivecard-inputchoice">InputChoice <a href="https://adaptivecards.io/explorer/Input.Choice.html">docs</a></h4>

| Argument name | Property | Type                     |
|---------------|----------|--------------------------|
| **title**     | title    | *str*, trans<sup>1</sup> |
| **value**     | value    | *str*, *int*             |
| lang_code     | -        | *str*                    |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="adaptivecard-choicesetinput">ChoiceSetInput <a href="https://adaptivecards.io/explorer/Input.ChoiceSet.html">docs</a></h4>

| Argument name   | Function              | Property      | Type                                                    |
|-----------------|-----------------------|---------------|---------------------------------------------------------|
| **choices**     | set_choices()         | choices       | *list* of InputChoice(s)<sup>1</sup>                    |
| is_multi_select | set_is_multi_select() | isMultiSelect | *bool*                                                  |
| style           | set_style()           | style         | ChoiceInputStyle<sup>2</sup>                            |
| value           | set_value()           | value         | *str*                                                   |
| wrap            | set_wrap()            | wrap          | *bool*                                                  |
| fallback        | set_fallback()        | fallback      | FallbackOption<sup>2</sup> or card element<sup>3</sup>  |
| separator       | set_separator()       | separator     | *bool*                                                  |
| spacing         | set_spacing()         | spacing       | SpacingStyle<sup>2</sup>                                |
| item_id         | set_id()              | id            | *str*                                                   |
| is_visible      | set_is_visible()      | isVisible     | *bool*                                                  |
| requires        | set_requires()        | requires      | *dict*                                                  |
| height          | set_height()          | height        | BlockElementHeight<sup>2</sup>                          |
| label           | set_label()           | label         | *str*, TextBlock<sup>4</sup>, RichTextBlock<sup>4</sup> |
| lang_code       | -                     | -             | *str*                                                   |

\[1\] `from django_actionable_messages.adaptive_cards.inputs import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[3\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

\[4\] `from django_actionable_messages.adaptive_cards.elements import ...`


<h3 id="adaptivecard-actions">Actions</h3>

**src**: `from django_actionable_messages.adaptive_card.actions import ...`

<h4 id="adaptivecard-openurl">OpenUrl <a href="https://adaptivecards.io/explorer/Action.OpenUrl.html">docs</a></h4>

| Argument name | Function         | Property  | Type                                                                               |
|---------------|------------------|-----------|------------------------------------------------------------------------------------|
| **url**       | set_url()        | url       | *str*                                                                              |
| title         | set_title()      | title     | *str*, trans<sup>3</sup>                                                           |
| icon_url      | set_icon_url()   | iconUrl   | *str*                                                                              |
| style         | set_style()      | style     | ActionStyle<sup>2</sup>                                                            |
| item_id       | set_id()         | id        | *str*                                                                              |
| fallback      | set_fallback()   | fallback  | FallbackOption<sup>2</sup> or action<sup>1</sup>(except TargetElement<sup>1</sup>) |
| tooltip       | set_tooltip()    | tooltip   | *str*                                                                              |
| is_enabled    | set_is_enabled() | isEnabled | *bool*                                                                             |
| mode          | set_mode()       | mode      | ActionMode<sup>2</sup>                                                             |
| requires      | set_requires()   | requires  | *dict*                                                                             |
| lang_code     | -                | -         | *str*                                                                              |

\[1\] `from django_actionable_messages.adaptive_cards.actions import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[3\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="adaptivecard-submit">Submit <a href="https://adaptivecards.io/explorer/Action.Submit.html">docs</a></h4>

| Argument name | Function         | Property  | Type                                                                               |
|---------------|------------------|-----------|------------------------------------------------------------------------------------|
| data          | set_data()       | data      | *str*, *dict*                                                                      |
| title         | set_title()      | title     | *str*, trans<sup>3</sup>                                                           |
| icon_url      | set_icon_url()   | iconUrl   | *str*                                                                              |
| style         | set_style()      | style     | ActionStyle<sup>2</sup>                                                            |
| item_id       | set_id()         | id        | *str*                                                                              |
| fallback      | set_fallback()   | fallback  | FallbackOption<sup>2</sup> or action<sup>1</sup>(except TargetElement<sup>1</sup>) |
| tooltip       | set_tooltip()    | tooltip   | *str*                                                                              |
| is_enabled    | set_is_enabled() | isEnabled | *bool*                                                                             |
| mode          | set_mode()       | mode      | ActionMode<sup>2</sup>                                                             |
| requires      | set_requires()   | requires  | *dict*                                                                             |
| lang_code     | -                | -         | *str*                                                                              |

\[1\] `from django_actionable_messages.adaptive_cards.actions import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[3\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="adaptivecard-showcard">ShowCard <a href="https://adaptivecards.io/explorer/Action.ShowCard.html">docs</a></h4>

| Argument name | Function         | Property  | Type                                                                               |
|---------------|------------------|-----------|------------------------------------------------------------------------------------|
| card          | set_card()       | card      | AdaptiveCard<sup>2</sup>                                                           |
| title         | set_title()      | title     | *str*, trans<sup>4</sup>                                                           |
| icon_url      | set_icon_url()   | iconUrl   | *str*                                                                              |
| style         | set_style()      | style     | ActionStyle<sup>3</sup>                                                            |
| item_id       | set_id()         | id        | *str*                                                                              |
| fallback      | set_fallback()   | fallback  | FallbackOption<sup>3</sup> or action<sup>1</sup>(except TargetElement<sup>1</sup>) |
| tooltip       | set_tooltip()    | tooltip   | *str*                                                                              |
| is_enabled    | set_is_enabled() | isEnabled | *bool*                                                                             |
| mode          | set_mode()       | mode      | ActionMode<sup>3</sup>                                                             |
| requires      | set_requires()   | requires  | *dict*                                                                             |
| lang_code     | -                | -         | *str*                                                                              |

\[1\] `from django_actionable_messages.adaptive_cards.actions import ...`

\[2\] `from django_actionable_messages.adaptive_cards.cards import ...`

\[3\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[4\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="adaptivecard-targetelement">TargetElement <a href="https://adaptivecards.io/explorer/TargetElement.html">docs</a></h4>

| Argument name   | Function          | Property   | Type   |
|-----------------|-------------------|------------|--------|
| **element_id**  | set_element_id()  | elementId  | *str*  |
| is_visible      | set_is_visible()  | isVisible  | *bool* |

<h4 id="adaptivecard-togglevisibility">ToggleVisibility <a href="https://adaptivecards.io/explorer/Action.ToggleVisibility.html">docs</a></h4>

| Argument name   | Function              | Property       | Type                                                                               |
|-----------------|-----------------------|----------------|------------------------------------------------------------------------------------|
| target_elements | set_target_elements() | targetElements | *list* of TargetElement<sup>1</sup>/*str*/trans<sup>3</sup> (can be mixed)         |
| title           | set_title()           | title          | *str*                                                                              |
| icon_url        | set_icon_url()        | iconUrl        | *str*                                                                              |
| style           | set_style()           | style          | ActionStyle<sup>2</sup>                                                            |
| item_id         | set_id()              | id             | *str*                                                                              |
| fallback        | set_fallback()        | fallback       | FallbackOption<sup>1</sup> or action<sup>1</sup>(except TargetElement<sup>1</sup>) |
| tooltip         | set_tooltip()         | tooltip        | *str*                                                                              |
| is_enabled      | set_is_enabled()      | isEnabled      | *bool*                                                                             |
| mode            | set_mode()            | mode           | ActionMode<sup>2</sup>                                                             |
| requires        | set_requires()        | requires       | *dict*                                                                             |
| lang_code       | -                     | -              | *str*                                                                              |

\[1\] `from django_actionable_messages.adaptive_cards.actions import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[3\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="adaptivecard-execute">Execute <a href="https://adaptivecards.io/explorer/Action.Execute.html">docs</a></h4>

| Argument name     | Function                | Property         | Type                                                                               |
|-------------------|-------------------------|------------------|------------------------------------------------------------------------------------|
| verb              | set_verb()              | verb             | *str*                                                                              |
| data              | set_data()              | data             | *str*, object                                                                      |
| associated_inputs | set_associated_inputs() | associatedInputs | AssociatedInputs<sup>1</sup>                                                       |
| title             | set_title()             | title            | *str*                                                                              |
| icon_url          | set_icon_url()          | iconUrl          | *str*                                                                              |
| style             | set_style()             | style            | ActionStyle<sup>1</sup>                                                            |
| fallback          | set_fallback()          | fallback         | FallbackOption<sup>1</sup> or action<sup>2</sup>(except TargetElement<sup>2</sup>) |
| tooltip           | set_tooltip()           | tooltip          | *str*                                                                              |
| is_enabled        | set_is_enabled()        | isEnabled        | *bool*                                                                             |
| mode              | set_mode()              | mode             | ActionMode<sup>1</sup>                                                             |
| requires          | set_requires()          | requires         | *dict*                                                                             |
| lang_code         | -                       | -                | *str*                                                                              |

\[1\] `from django_actionable_messages.adaptive_card.utils import ...`

\[2\] `from django_actionable_messages.adaptive_card.actions import ...`

<h3 id="adaptivecard-containers">Containers</h3>

**src**: `from django_actionable_messages.adaptive_card.containers import ...`

<h4 id="adaptivecard-actionset">ActionSet <a href="https://adaptivecards.io/explorer/ActionSet.html">docs</a></h4>

| Argument name | Function         | Property  | Type                                                   |
|---------------|------------------|-----------|--------------------------------------------------------|
| actions       | add_actions()    | actions   | action or *list* of actions(see docs)                  |
| fallback      | set_fallback()   | fallback  | FallbackOption<sup>1</sup> or card element<sup>2</sup> |
| separator     | set_separator()  | separator | *bool*                                                 |
| spacing       | set_spacing()    | spacing   | SpacingStyle<sup>1</sup>                               |
| item_id       | set_id()         | id        | *str*                                                  |
| is_visible    | set_is_visible() | isVisible | *bool*                                                 |
| requires      | set_requires()   | requires  | *dict*                                                 |
| height        | set_height()     | height    | BlockElementHeight<sup>1</sup>                         |
| lang_code     | -                | -         | *str*                                                  |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[2\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

<h4 id="adaptivecard-container">Container <a href="https://adaptivecards.io/explorer/Container.html">docs</a></h4>

| Argument name              | Function                         | Property                 | Type                                                   |
|----------------------------|----------------------------------|--------------------------|--------------------------------------------------------|
| items                      | add_items()                      | items                    | item or *list* of items(see docs)                      |
| select_action              | set_select_action()              | selectAction             | any action(see docs)                                   |
| style                      | set_style()                      | style                    | Style<sup>2</sup>                                      |
| vertical_content_alignment | set_vertical_content_alignment() | verticalContentAlignment | VerticalAlignment<sup>2</sup>                          |
| bleed                      | set_bleed()                      | bleed                    | *bool*                                                 |
| background_image           | set_background_image()           | backgroundImage          | BackgroundImage<sup>1</sup>                            |
| min_height                 | set_min_height()                 | minHeight                | *str*                                                  |
| rtl                        | set_rtl()                        | rtl                      | *bool*                                                 |
| fallback                   | set_fallback()                   | fallback                 | FallbackOption<sup>2</sup> or card element<sup>3</sup> |
| separator                  | set_separator()                  | separator                | *bool*                                                 |
| spacing                    | set_spacing()                    | spacing                  | SpacingStyle<sup>2</sup>                               |
| item_id                    | set_id()                         | id                       | *str*                                                  |
| is_visible                 | set_is_visible()                 | isVisible                | *bool*                                                 |
| requires                   | set_requires()                   | requires                 | *dict*                                                 |
| height                     | set_height()                     | height                   | BlockElementHeight<sup>2</sup>                         |
| lang_code                  | -                                | -                        | *str*                                                  |

\[1\] `from django_actionable_messages.adaptive_cards.types import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[3\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

<h4 id="adaptivecard-column">Column <a href="https://adaptivecards.io/explorer/Column.html">docs</a></h4>

| Argument name              | Function                         | Property                 | Type                                             |
|----------------------------|----------------------------------|--------------------------|--------------------------------------------------|
| items                      | add_items()                      | items                    | item or *list* of items(see docs)                |
| background_image           | set_background_image()           | backgroundImage          | *str*, BackgroundImage<sup>2</sup>               |
| bleed                      | set_bleed()                      | bleed                    | *bool*                                           |
| fallback                   | set_fallback()                   | fallback                 | FallbackOption<sup>3</sup> or Column<sup>1</sup> |
| min_height                 | set_min_height()                 | minHeight                | *str*                                            |
| rtl                        | set_rtl()                        | rtl                      | *bool*                                           |
| separator                  | set_separator()                  | separator                | *bool*                                           |
| spacing                    | set_spacing()                    | spacing                  | SpacingStyle<sup>3</sup>                         |
| select_action              | set_select_action()              | selectAction             | see docs                                         |
| style                      | set_style()                      | style                    | Style<sup>3</sup>                                |
| vertical_content_alignment | set_vertical_content_alignment() | verticalContentAlignment | VerticalAlignment<sup>3</sup>                    |
| width                      | set_width()                      | width                    | *str*, *int*, Width<sup>3</sup>                  |
| item_id                    | set_id()                         | id                       | *str*                                            |
| is_visible                 | set_is_visible()                 | isVisible                | *bool*                                           |
| requires                   | set_requires()                   | requires                 | *dict*                                           |
| lang_code                  | -                                | -                        | *str*                                            |

\[1\] `from django_actionable_messages.adaptive_cards.containers import ...`

\[2\] `from django_actionable_messages.adaptive_cards.types import ...`

\[3\] `from django_actionable_messages.adaptive_cards.utils import ...`

<h4 id="adaptivecard-columnset">ColumnSet <a href="https://adaptivecards.io/explorer/ColumnSet.html">docs</a></h4>

| Argument name | Function            | Property     | Type                                                   |
|---------------|---------------------|--------------|--------------------------------------------------------|
| **columns**   | add_columns()       | columns      | Column<sup>1</sup> or *list* of Column(s)<sup>1</sup>  |
| select_action | set_select_action() | selectAction | see docs                                               |
| style         | set_style()         | style        | Style<sup>2</sup>                                      |
| bleed         | set_bleed()         | bleed        | *bool*                                                 |
| min_height    | set_min_height()    | minHeight    | *str*                                                  |
| fallback      | set_fallback()      | fallback     | FallbackOption<sup>2</sup> or card element<sup>3</sup> |
| separator     | set_separator()     | separator    | *bool*                                                 |
| spacing       | set_spacing()       | spacing      | SpacingStyle<sup>2</sup>                               |
| item_id       | set_id()            | id           | *str*                                                  |
| is_visible    | set_is_visible()    | isVisible    | *bool*                                                 |
| requires      | set_requires()      | requires     | *dict*                                                 |
| height        | set_height()        | height       | BlockElementHeight<sup>2</sup>                         |
| lang_code     | -                   | -            | *str*                                                  |

\[1\] `from django_actionable_messages.adaptive_cards.containers import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[3\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

<h4 id="adaptivecard-fact">Fact <a href="https://adaptivecards.io/explorer/Fact.html">docs</a></h4>

| Argument name | Property | Type                     |
|---------------|----------|--------------------------|
| **title**     | title    | *str*, trans<sup>1</sup> |
| **value**     | value    | *str*, trans<sup>1</sup> |
| lang_code     | -        | *str*                    |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="adaptivecard-factset">FactSet <a href="https://adaptivecards.io/explorer/FactSet.html">docs</a></h4>

| Argument name | Function         | Property  | Type                                                   |
|---------------|------------------|-----------|--------------------------------------------------------|
| facts         | add_facts()      | facts     | Fact<sup>1</sup> or *list* of Fact(s)<sup>1</sup>      |
| fallback      | set_fallback()   | fallback  | FallbackOption<sup>2</sup> or card element<sup>3</sup> |
| separator     | set_separator()  | separator | *bool*                                                 |
| spacing       | set_spacing()    | spacing   | SpacingStyle<sup>2</sup>                               |
| item_id       | set_id()         | id        | *str*                                                  |
| is_visible    | set_is_visible() | isVisible | *bool*                                                 |
| requires      | set_requires()   | requires  | *dict*                                                 |
| height        | set_height()     | height    | BlockElementHeight<sup>2</sup>                         |
| lang_code     | -                | -         | *str*                                                  |

\[1\] `from django_actionable_messages.adaptive_cards.containers import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[3\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

<h4 id="adaptivecard-imageset">ImageSet <a href="https://adaptivecards.io/explorer/ImageSet.html">docs</a></h4>

| Argument name | Function         | Property  | Type                                                   |
|---------------|------------------|-----------|--------------------------------------------------------|
| images        | add_images()     | images    | Image<sup>1</sup> or *list* of Image(s)<sup>1</sup>    |
| image_size    | set_image_size() | imageSize | ImageSize<sup>2</sup>                                  |
| fallback      | set_fallback()   | fallback  | FallbackOption<sup>2</sup> or card element<sup>3</sup> |
| separator     | set_separator()  | separator | *bool*                                                 |
| spacing       | set_spacing()    | spacing   | SpacingStyle<sup>2</sup>                               |
| item_id       | set_id()         | id        | *str*                                                  |
| is_visible    | set_is_visible() | isVisible | *bool*                                                 |
| requires      | set_requires()   | requires  | *dict*                                                 |
| height        | set_height()     | height    | BlockElementHeight<sup>2</sup>                         |
| lang_code     | -                | -         | *str*                                                  |

\[1\] `from django_actionable_messages.adaptive_cards.elements import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[3\] `from django_actionable_messages.adaptive_cards.elements import ...`

| Type         | All except           | Import                                                                 |
|--------------|----------------------|------------------------------------------------------------------------|
| `containers` | Fact, Column         | `from django_actionable_messages.adaptive_cards.containers import ...` |
| `elements`   | MediaSource, TextRun | `from django_actionable_messages.adaptive_cards.elements import ...`   |
| `inputs`     | InputChoice          | `from django_actionable_messages.adaptive_cards.inputs import ...`     |

<h4 id="adaptivecard-tablecell">TableCell <a href="https://adaptivecards.io/explorer/TableCell.html">docs</a></h4>

| Argument name              | Function                         | Property                 | Type                                                                                         |
|----------------------------|----------------------------------|--------------------------|----------------------------------------------------------------------------------------------|
| select_action              | set_select_action()              | selectAction             | Execute<sup>1</sup>, OpenUrl<sup>1</sup>, Submit<sup>1</sup> or ToggleVisibility<sup>1</sup> |
| style                      | set_style()                      | style                    | Style<sup>2</sup>                                                                            |
| vertical_content_alignment | set_vertical_content_alignment() | verticalContentAlignment | VerticalAlignment<sup>2</sup>                                                                |
| bleed                      | set_bleed()                      | bleed                    | *bool*                                                                                       |
| background_image           | set_background_image()           | backgroundImage          | BackgroundImage<sup>3</sup> or *str*                                                         |
| min_height                 | set_min_height()                 | minHeight                | *str*                                                                                        |
| rtl                        | set_rtl()                        | rtl                      | *bool*                                                                                       |
| lang_code                  | -                                | -                        | *str*                                                                                        |

\[1\] `from django_actionable_messages.adaptive_cards.actions import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[3\] `from django_actionable_messages.adaptive_cards.types import ...`

<h4 id="adaptivecard-tablerow">TableRow</h4>

| Argument name | Function    | Property | Type                  |
|---------------|-------------|----------|-----------------------|
| cells         | add_cells() | cells    | TableCell<sup>1</sup> |
| lang_code     | -           | -        | *str*                 |

\[1\] `from django_actionable_messages.adaptive_cards.containers import ...`

<h4 id="adaptivecard-table">Table <a href="https://adaptivecards.io/explorer/Table.html">docs</a></h4>

| Argument name                     | Function                                | Property                       | Type                                                   |
|-----------------------------------|-----------------------------------------|--------------------------------|--------------------------------------------------------|
| columns                           | add_columns()                           | columns                        | *dict*                                                 |
| rows                              | add_rows()                              | rows                           | TableRow<sup>1</sup> or *list* of TableRow<sup>1</sup> |
| horizontal_cell_content_alignment | set_horizontal_cell_content_alignment() | horizontalCellContentAlignment | HorizontalAlignment<sup>2</sup>                        |
| vertical_cell_content_alignment   | set_vertical_cell_content_alignment()   | verticalCellContentAlignment   | VerticalAlignment<sup>2</sup>                          |
| first_row_as_header               | set_first_row_as_header()               | firstRowAsHeader               | *bool*                                                 |
| show_grid_lines                   | set_show_grid_lines()                   | showGridLines                  | *bool*                                                 |
| grid_style                        | set_grid_style()                        | style                          | Style<sup>2</sup>                                      |
| height                            | set_height()                            | height                         | BlockElementHeight<sup>2</sup>                         |
| fallback                          | set_fallback()                          | fallback                       | FallbackOption<sup>2</sup> or card element<sup>3</sup> |
| separator                         | set_separator()                         | separator                      | *bool*                                                 |
| spacing                           | set_spacing()                           | spacing                        | SpacingStyle<sup>2</sup>                               |
| item_id                           | set_id()                                | id                             | *str*                                                  |
| is_visible                        | set_is_visible()                        | isVisible                      | *bool*                                                 |
| requires                          | set_requires()                          | requires                       | *dict*                                                 |
| lang_code                         | -                                       | -                              | *str*                                                  |

\[1\] `from django_actionable_messages.adaptive_cards.containers import ...`

\[2\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[3\] `from django_actionable_messages.adaptive_cards.elements import ...`

<h3 id="adaptivecard-types">Types</h3>

**src**: `from django_actionable_messages.adaptive_card.types import ...`

<h4 id="adaptivecard-backgroundimage">BackgroundImage <a href="https://adaptivecards.io/explorer/BackgroundImage.html">docs</a></h4>

| Argument name        | Function                   | Property            | Type                            |
|----------------------|----------------------------|---------------------|---------------------------------|
| **url**              | set_url()                  | url                 | *str*                           |
| fill_mode            | set_fill_mode()            | fillMode            | FillMode<sup>1</sup>            |
| horizontal_alignment | set_horizontal_alignment() | horizontalAlignment | HorizontalAlignment<sup>1</sup> |
| vertical_alignment   | set_vertical_alignment()   | verticalAlignment   | VerticalAlignment<sup>1</sup>   |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

<h4 id="adaptivecard-refresh">Refresh <a href="https://adaptivecards.io/explorer/Refresh.html">docs</a></h4>

| Argument name | Function        | Property | Type                |
|---------------|-----------------|----------|---------------------|
| action        | set_action()    | Execute  | Execute<sup>1</sup> |
| user_ids      | set_user_ids()  | list     | list of *str*       |

\[1\] `from django_actionable_messages.adaptive_cards.actions import ...`

<h4 id="adaptivecard-tokenexchangeresource">TokenExchangeResource <a href="https://adaptivecards.io/explorer/TokenExchangeResource.html">docs</a></h4>

| Argument name    | Function           | Property    | Type   |
|------------------|--------------------|-------------|--------|
| **token_id**     | set_id()           | id          | *str*  |
| **uri**          | set_user_uri()     | uri         | *str*  |
| **provider_id**  | set_provider_id()  | providerId  | *str*  |

<h4 id="adaptivecard-authcardbutton">AuthCardButton <a href="https://adaptivecards.io/explorer/AuthCardButton.html">docs</a></h4>

| Argument name | Function    | Property | Type   |
|---------------|-------------|----------|--------|
| **btn_type**  | -           | type     | *str*  |
| **value**     | -           | value    | *str*  |
| title         | set_title() | title    | *str*  |
| image         | set_image() | image    | *str*  |

<h4 id="adaptivecard-authentication">Authentication <a href="https://adaptivecards.io/explorer/Authentication.html">docs</a></h4>

| Argument name           | Function                      | Property              | Type                                 |
|-------------------------|-------------------------------|-----------------------|--------------------------------------|
| text                    | set_text()                    | text                  | *str*                                |
| connection_name         | set_connection_name()         | connectionName        | *str*                                |
| token_exchange_resource | set_token_exchange_resource() | tokenExchangeResource | TokenExchangeResource<sup>1</sup>    |
| buttons                 | set_buttons()                 | buttons               | *list* of AuthCardButton<sup>1</sup> |

\[1\] `from django_actionable_messages.adaptive_cards.types import ...`

<h3 id="adaptivecard-cards">Cards</h3>

**src**: `from django_actionable_messages.adaptive_card.cards import ...`

<h4 id="adaptivecard-adaptivecard">AdaptiveCard <a href="https://adaptivecards.io/explorer/AdaptiveCard.html">docs</a></h4>

| Argument name              | Function                         | Property                 | Type                                  |
|----------------------------|----------------------------------|--------------------------|---------------------------------------|
| version                    | set_version()                    | version                  | *str*, SCHEMA<sup>1</sup>             |
| schema                     | set_schema()                     | $schema                  | *str*                                 |
| refresh                    | set_refresh()                    | refresh                  | Refresh<sup>3</sup>                   |
| authentication             | set_authentication()             | authentication           | Authentication<sup>3</sup>            |
| inputs                     | add_elements()                   | inputs                   | input or *list* of inputs(see docs)   |
| actions                    | add_actions()                    | actions                  | action or *list* of actions(see docs) |
| select_action              | set_select_action()              | selectAction             | see docs                              |
| style                      | set_style()                      | style                    | Style<sup>1</sup>                     |
| hide_original_body         | set_hide_original_body()         | hideOriginalBody         | *bool*                                |
| fallback_text              | set_fallback_text()              | fallbackText             | *str*                                 |
| background_image           | set_background_image()           | backgroundImage          | *str*, Image<sup>2</sup>              |
| min_height                 | set_min_height()                 | minHeight                | *str*                                 |
| speak                      | set_speak()                      | speak                    | *str*                                 |
| lang                       | set_lang()                       | lang                     | *str*                                 |
| rtl                        | set_rtl()                        | rtl                      | *bool*                                |
| vertical_content_alignment | set_vertical_content_alignment() | verticalContentAlignment | VerticalAlignment<sup>1</sup>         |
| lang_code                  | -                                | -                        | *str*                                 |

\[1\] `from django_actionable_messages.adaptive_cards.utils import ...`

\[2\] `from django_actionable_messages.adaptive_cards.elements import ...`

\[3\] `from django_actionable_messages.adaptive_cards.types import ...`

<h2 id="messagecard">MessageCard</h2>

[Legacy actionable message card reference](https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference)

<h3 id="messagecard-elements">Elements</h3>

**src**: `from django_actionable_messages.message_card.elements import ...`

<h4 id="messagecard-header">Header <a href="https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference#header">docs</a></h4>

| Argument name | Property | Type          |
|---------------|----------|---------------|
| **name**      | name     | *str*         |
| **value**     | value    | *str*, *int*  |

<h4 id="messagecard-fact">**Fact**</h4>

| Argument name | Property | Type                     |
|---------------|----------|--------------------------|
| **name**      | name     | *str*, trans<sup>1</sup> |
| **value**     | value    | *str*, trans<sup>1</sup> |
| lang_code     | -        | *str*                    |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="messagecard-heroimage">HeroImage <a href="https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference#image-object">docs</a></h4>

| Argument name | Function    | Property | Type                     |
|---------------|-------------|----------|--------------------------|
| **url**       | set_url()   | image    | *str*                    |
| title         | set_title() | title    | *str*, trans<sup>1</sup> |
| lang_code     | -           | -        | *str*                    |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="messagecard-inputchoice">InputChoice</h4>

| Argument name | Property | Type                     |
|---------------|----------|--------------------------|
| **name**      | display  | *str*, trans<sup>1</sup> |
| **value**     | value    | *str*, *int*             |
| lang_code     | -        | *str*                    |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="messagecard-actiontarget">ActionTarget</h4>

| Argument name | Property | Type               |
|---------------|----------|--------------------|
| **os_type**   | os       | OSType<sup>1</sup> |
| url           | uri      | *str*              |
| lang_code     | -        | *str*              |

\[1\] `from django_actionable_messages.message_cards.utils import ...`

<h3 id="messagecard-inputs">Inputs</h3>

**src**: `from django_actionable_messages.message_card.inputs import ...`

<h4 id="messagecard-textinput">TextInput <a href="https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference#textinput">docs</a></h4>

| Argument name | Function           | Property    | Type                     |
|---------------|--------------------|-------------|--------------------------|
| max_length    | set_max_length()   | maxLength   | *int*                    |
| is_multiline  | set_is_multiline() | isMultiline | *bool*                   |
| input_id      | set_id()           | id          | *str*                    |
| title         | set_title()        | title       | *str*, trans<sup>1</sup> |
| value         | set_value()        | value       | *str*                    |
| is_required   | set_is_required()  | isRequired  | *bool*                   |
| lang_code     | -                  | -           | *str*                    |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="messagecard-dateinput">DateInput <a href="https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference#dateinput">docs</a></h4>

| Argument name | Function           | Property   | Type                     |
|---------------|--------------------|------------|--------------------------|
| include_time  | set_include_time() | maxLength  | *bool*                   |
| input_id      | set_id()           | id         | *str*                    |
| title         | set_title()        | title      | *str*, trans<sup>1</sup> |
| value         | set_value()        | value      | *str*                    |
| is_required   | set_is_required()  | isRequired | *bool*                   |
| lang_code     | -                  | -          | *str*                    |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="messagecard-multichoiceinput">MultiChoiceInput <a href="https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference#multichoiceinput">docs</a></h4>

| Argument name   | Function              | Property        | Type                                 |
|-----------------|-----------------------|-----------------|--------------------------------------|
| **choices**     | add_choices()         | choices         | *list* of InputChoice(s)<sup>1</sup> |
| is_multi_select | set_is_multi_select() | isMultiSelect   | *bool*                               |
| style           | set_style()           | style           | ChoiceStyle<sup>2</sup>              |
| input_id        | set_id()              | id              | *str*                                |
| title           | set_title()           | title           | *str*, trans<sup>3</sup>             |
| value           | set_value()           | value           | *str*                                |
| is_required     | set_is_required()     | isRequired      | *bool*                               |
| lang_code       | -                     | -               | *str*                                |

Other functions

| Name          | Property | Type                     |
|---------------|----------|--------------------------|
| add_choice()  | choices  | InputChoice<sup>1</sup>  |

\[1\] `from django_actionable_messages.message_cards.inputs import ...`

\[2\] `from django_actionable_messages.message_cards.utils import ...`

\[3\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h3 id="messagecard-actions">Actions</h3>

**src**: `from django_actionable_messages.message_card.actions import ...`

<h4 id="messagecard-openuri">OpenUri <a href="https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference#openuri-action">docs</a></h4>

| Argument name | Function      | Property | Type                               |
|---------------|---------------|----------|------------------------------------|
| **name**      | set_name()    | name     | *str*, trans<sup>2</sup>           |
| targets       | add_targets() | targets  | *list* of ActionTarget<sup>1</sup> |
| lang_code     | -             | -        | *str*                              |

Other functions

| Name          | Property | Type                      |
|---------------|----------|---------------------------|
| add_target()  | targets  | ActionTarget<sup>1</sup>  |

\[1\] `from django_actionable_messages.message_cards.elements import ...`

\[2\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="messagecard-httppost">HttpPOST <a href="https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference#httppost-action">docs</a></h4>

| Argument name      | Function                | Property        | Type                                                  |
|--------------------|-------------------------|-----------------|-------------------------------------------------------|
| **name**           | set_name()              | name            | *str*, trans<sup>2</sup>                              |
| **target**         | set_target()            | targets         | *str*                                                 |
| headers            | add_headers()           | headers         | Header<sup>1</sup> or *list* of Header(s)<sup>1</sup> |
| body               | set_body()              | body            | *str*                                                 |
| body_content_type  | set_body_content_type() | bodyContentType | *str*                                                 |
| lang_code          | -                       | -               | *str*                                                 |

\[1\] `from django_actionable_messages.message_cards.elements import ...`

\[2\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="messagecard-invokeaddincommand">InvokeAddInCommand <a href="https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference#invokeaddincommand-action">docs</a></h4>

| Argument name          | Function                         | Property              | Type                     |
|------------------------|----------------------------------|-----------------------|--------------------------|
| **name**               | set_name()                       | name                  | *str*, trans<sup>1</sup> |
| **add_in_id**          | set_add_in_id()                  | addInId               | *str*                    |
| **desktop_command_id** | set_desktop_command_id()         | desktopCommandId      | *str*                    |
| initialization_context | set_set_initialization_context() | initializationContext | *dict*                   |
| lang_code              | -                                | -                     | *str*                    |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="messagecard-actioncard">ActionCard <a href="https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference#actioncard-action">docs</a></h4>

| Argument name | Function       | Property | Type                                  |
|---------------|----------------|----------|---------------------------------------|
| **name**      | set_name()     | name     | *str*, trans<sup>1</sup>              |
| inputs        | add_inputs()   | inputs   | input or *list* of inputs(see docs)   |
| actions       | add_actions()  | actions  | action or *list* of actions(see docs) |
| lang_code     | -              | -        | *str*                                 |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h3 id="messagecard-sections">Sections</h3>

**src**: `from django_actionable_messages.message_card.sections import ...`

<h4 id="messagecard-section">Section <a href="https://docs.microsoft.com/en-gb/outlook/actionable-messages/message-card-reference#section-fields">docs</a></h4>

| Argument name     | Function                | Property         | Type                                              |
|-------------------|-------------------------|------------------|---------------------------------------------------|
| start_group       | set_start_group()       | startGroup       | *bool*                                            |
| title             | set_title()             | title            | *str*, trans<sup>2</sup>                          |
| text              | set_text()              | text             | *str*, trans<sup>2</sup>                          |
| activity_image    | set_activity_image()    | activityImage    | *str*                                             |
| activity_title    | set_activity_title()    | activityTitle    | *str*, trans<sup>2</sup>                          |
| activity_subtitle | set_activity_subtitle() | activitySubtitle | *str*, trans<sup>2</sup>                          |
| activity_text     | set_activity_text()     | activityText     | *str*, trans<sup>2</sup>                          |
| hero_image        | set_hero_image()        | heroImage        | HeroImage<sup>2</sup>                             |
| facts             | add_facts()             | facts            | Fact(s)<sup>1</sup> or *list* of Fact<sup>1</sup> |
| actions           | add_potential_actions() | potentialAction  | action or *list* of actions(see docs)             |
| lang_code         | -                       | -                | *str*                                             |

Other functions:

| Name                                       | Property                                                     | Type  |
|--------------------------------------------|--------------------------------------------------------------|-------|
| set_activity(image, title, subtitle, text) | activityImage, activityTitle, activitySubtitle, activityText | *str* |

\[1\] `from django_actionable_messages.message_cards.elements import ...`

\[2\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h3 id="messagecard-cards">Cards</h3>

**src**: `from django_actionable_messages.message_card.cards import ...`

<h4 id="messagecard-messagecard">MessageCard</h4>

| Argument name        | Function                 | Property         | Type                                                  |
|----------------------|--------------------------|------------------|-------------------------------------------------------|
| title                | set_title()              | title            | *str*, trans<sup>2</sup>                              |
| text                 | set_text()               | text             | *str*, trans<sup>2</sup>                              |
| originator           | set_originator()         | originator       | *str*                                                 |
| summary              | set_summary()            | summary          | *str*, trans<sup>2</sup>                              |
| theme_color          | set_theme_color()        | themeColor       | *str*                                                 |
| correlation_id       | set_correlation_id()     | correlationId    | *str*                                                 |
| auto_correlation_id* | -                        | correlationId    | *bool* (default: *True*)                              |
| expected_actors      | set_expected_actors()    | expectedActors   | *list* of emails                                      |
| hide_original_body   | set_hide_original_body() | hideOriginalBody | *bool*                                                |
| sections             | add_sections()           | sections         | Section<sup>1</sup> or *list* of Sections<sup>1</sup> |
| actions              | add_actions()            | potentialAction  | action<sup>3</sup> or *list* of actions<sup>3</sup>   |
| lang_code            | -                        | -                | *str*                                                 |

Other functions:

| Name                   | Property        | Type                    |
|------------------------|-----------------|-------------------------|
| add_expected_actors()  | expectedActors  | *str* or list of *str*  |

\[1\] `from django_actionable_messages.message_cards.sections import ...`

\[2\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

\[3\] `from django_actionable_messages.message_cards.actions import ...`

<h2 id="herocard">HeroCard</h2>

<h3 id="herocard-elements">Elements</h3>

<h4 id="herocard-openurl">OpenUrl</h4>

| Argument name | Function | Property | Type                     |
|---------------|----------|----------|--------------------------|
| **title**     | -        | title    | *str*, trans<sup>1</sup> |
| **url**       | -        | value    | *str*                    |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h4 id="herocard-Image">Image</h4>

| Argument name | Function | Property | Type                      |
|---------------|----------|----------|---------------------------|
| **url**       | -        | value    | *str*                     |
| alt           | -        | alt      | *str*, trans<sup>1</sup>  |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

<h3 id="herocard-cards">Cards</h3>

**src**: `from django_actionable_messages.msteams_cards.cards import HeroCard`

<h4 id="herocard-herocard">HeroCard <a href="https://docs.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-reference#hero-card">docs</a></h4>

| Argument name | Function       | Property | Type                                                  |
|---------------|----------------|----------|-------------------------------------------------------|
| title         | set_title()    | title    | *str*, trans<sup>1</sup>                              |
| subtitle      | set_subtitle() | subtitle | *str*, trans<sup>1</sup>                              |
| text          | set_text()     | text     | *str*, trans<sup>1</sup>                              |
| images        | add_images()   | images   | Image<sup>2</sup> or *list* of Images<sup>2</sup>     |
| buttons       | add_buttons()  | buttons  | OpenUrl<sup>3</sup> or *list* of OpenUrls<sup>3</sup> |
| lang_code     | -              | -        | *str*                                                 |

\[1\] any translation like `from django.utils.translation import gettext, gettext_lazy, ...`

\[2\] `from django_actionable_messages.msteams_cards.elements import Image`

\[3\] `from django_actionable_messages.msteams_cards.elements import OpenUrl`

<h2 id="thumbnailcard">ThumbnailCard</h2>

<h3 id="thumbnailcard-elements">Elements</h3>

see HeroCard [Elements](#herocard-elements) section

<h3 id="thumbnailcard-cards">Cards</h3>

**src**: `from django_actionable_messages.msteams_cards.cards import ThumbnailCard`

<h4 id="thumbnailcard-thumbnailcard">ThumbnailCard <a href="https://docs.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-reference#thumbnail-card">docs</a></h4>

see HeroCard [HeroCard](#herocard-herocard) section
