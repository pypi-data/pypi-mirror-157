from datetime import datetime
from pydantic import BaseModel
from typing import Literal, List, Union, Optional


class File(BaseModel):
    file_id: str
    file_name: str
    size: str


class Chat(BaseModel):
    chat_id: str
    chat_type: Literal['User', 'Bot', 'Group', 'Channel']
    user_id: str
    first_name: str
    last_name: str
    title: str
    username: str


class ForwardedFrom(BaseModel):
    type_from: Literal['User', 'Channel', 'Bot']
    message_id: str
    from_chat_id: str
    from_sender_id: str


class PaymentStatus(BaseModel):
    payment_id: str
    status: Literal['Paid', 'NotPaid']


class MessageTextUpdate(BaseModel):
    message_id: str
    text: str


class Bot(BaseModel):
    bot_id: str
    bot_title: str
    avatar: File
    description: str
    username: str
    start_message: datetime
    share_url: str


class BotCommand(BaseModel):
    command: str
    description: str


class Sticker(BaseModel):
    sticker_id: str
    file: File
    emoji_character: str


class ContactMessage(BaseModel):
    phone_number: str
    first_name: str
    last_name: str


class PollStatus(BaseModel):
    state: Literal['Open', 'Closed']
    selection_index: int
    percent_vote_options: List[int]
    total_vote: int
    show_total_votes: bool


class Poll(BaseModel):
    question: str
    options: List[str]
    poll_status: PollStatus


class Location(BaseModel):
    longitude: str
    latitude: str


class LiveLocation(BaseModel):
    start_time: datetime
    live_period: int  # In Second
    current_location: Location
    user_id: str
    status: Literal['Stopped', 'Live']
    last_update_time: datetime


class ButtonSelectionItem(BaseModel):
    text: str
    image_url: Optional[str]
    type: Literal['TextOnly', 'TextImgThu', 'TextImgBig'] = 'TextOnly'


class ButtonSelection(BaseModel):
    selection_id: Optional[str]
    search_type: Literal['None', 'Local', 'Api'] = 'None'
    get_type: Literal['Local', 'Api'] = 'Local'
    items: List[ButtonSelectionItem]
    is_multi_selection: bool = False
    columns_count: int = 1
    title: Optional[str]  # default is button_text of its parent


class ButtonCalendar(BaseModel):
    default_value: Optional[str]
    type: Literal['DatePersian', 'DateGregorian']
    min_year: int = 0
    max_year: int = 0
    title: Optional[str]  # default is button_text of its parent


class ButtonNumberPicker(BaseModel):
    min_value: int = 0
    max_value: int = 100
    default_value: Union[int, None]
    title: Optional[str]  # default is button_text of its parent


class ButtonStringPicker(BaseModel):
    items: List[str]
    default_value: Optional[str]
    title: Optional[str]  # default is button_text of its parent


class ButtonTextbox(BaseModel):
    type_line: Literal['SingleLine', 'MultiLine'] = 'SingleLine'
    type_keypad: Literal['String', 'Number'] = 'String'
    place_holder: Optional[str]
    default_value: Optional[str]
    title: Optional[str]  # default is button_text of its parent


class ButtonLocation(BaseModel):
    default_pointer_location: Optional[Location]
    default_map_location: Optional[Location]
    type: Literal['Picker', 'View'] = 'Picker'
    title: str
    location_image_url: str


# class ButtonLink(BaseModel):
#     type: Literal['']


class AuxData(BaseModel):
    start_id: Optional[str]
    button_id: Optional[str]


class Button(BaseModel):
    id: str
    type: Literal[
        'Simple', 'Selection', 'Calendar', 'NumberPicker', 'StringPicker', 'Location', 'Payment',
        'CameraImage', 'CameraVideo', 'GalleryImage', 'GalleryVideo', 'File', 'Audio', 'RecordAudio',
        'MyPhoneNumber', 'MyLocation', 'Textbox', 'Link', 'AskMyPhoneNumber', 'AskLocation', 'Barcode'] = 'Simple'
    button_text: str
    button_selection: Optional[ButtonSelection]
    button_calendar: Optional[ButtonCalendar]
    button_number_picker: Optional[ButtonNumberPicker]
    button_string_picker: Optional[ButtonStringPicker]
    button_location: Optional[ButtonLocation]
    button_textbox: Optional[ButtonTextbox]
    button_link: Optional[dict]


class KeypadRow(BaseModel):
    buttons: List[Button]


class Keypad(BaseModel):
    rows: List[KeypadRow]
    resize_keyboard: Optional[bool]
    on_time_keyboard: Optional[bool]


class MessageKeypadUpdate(BaseModel):
    message_id: str
    inline_keypad: Keypad


class Message(BaseModel):
    message_id: str
    text: Optional[str]
    time: int
    is_edited: bool
    sender_type: Literal['User', 'Bot']
    sender_id: str

    aux_data: Optional[AuxData] = AuxData()
    file: Optional[File]
    reply_to_message_id: Optional[str]
    forwarded_from: Optional[ForwardedFrom]
    forwarded_no_link: Optional[str]
    location: Optional[Location]
    sticker: Optional[Sticker]
    contact_message: Optional[ContactMessage]
    poll: Optional[Poll]
    live_location: Optional[LiveLocation]


class Update(BaseModel):
    type: Literal['UpdatedMessage', 'NewMessage', 'RemovedMessage', 'StartedBot', 'StoppedBot', 'UpdatedPayment']
    chat_id: str
    removed_message_id: Optional[str]
    new_message: Message
    updated_message: Optional[Message]
    updated_payment: Optional[PaymentStatus]


class InlineMessage(BaseModel):
    sender_id: str
    text: str
    file: Optional[File]
    location: Optional[Location]
    aux_data: AuxData
    message_id: str
    chat_id: str
