from agentmake import agentmake, listResources, DEVELOPER_MODE, DEFAULT_AI_BACKEND, SUPPORTED_AI_BACKENDS, AnthropicAI, AzureAI, AzureAnyAI, CohereAI, OpenaiCompatibleAI, DeepseekAI, GenaiAI, GithubAI, GithubAnyAI, GoogleaiAI, GroqAI, LlamacppAI, MistralAI, OllamaAI, OpenaiAI, XaiAI
from pydoc import pipepager
import pyperclip, shutil, markdown, os
messages = []
backends = {
    "anthropic": AnthropicAI,
    "azure": AzureAI,
    "azure_any": AzureAnyAI,
    "cohere": CohereAI,
    "custom": OpenaiCompatibleAI,
    "deepseek": DeepseekAI,
    "genai": GenaiAI,
    "github": GithubAI,
    "github_any": GithubAnyAI,
    "googleai": GoogleaiAI,
    "groq": GroqAI,
    "llamacpp": LlamacppAI,
    "mistral": MistralAI,
    "ollama": OllamaAI,
    "openai": OpenaiAI,
    "vertexai": GenaiAI,
    "xai": XaiAI,
  }

import time
from dataclasses import asdict, dataclass
from typing import Callable, Literal, Optional

import mesop as me

Role = Literal["user", "bot"]

_APP_TITLE = "AgentMake Studio"
_BOT_AVATAR_LETTER = "AI"
_EMPTY_CHAT_MESSAGE = "Get started with an example"
_EXAMPLE_USER_QUERIES = (
  "Explain in a friendly manner:\n...",
  "Rewrite the following content in professional tone:\n...",
  "Translate the following content into ...",
)
_CHAT_MAX_WIDTH = "800px"
_MOBILE_BREAKPOINT = 640

_TEMPERATURE_MIN = 0.0
_TEMPERATURE_MAX = 2.0
_TOKEN_LIMIT_MIN = 1
_STYLE_INPUT_WIDTH = me.Style(width="100%")


@dataclass(kw_only=True)
class ChatMessage:
  """Chat message metadata."""
  role: Role = "user"
  content: str = ""
  edited: bool = True
  # 1 is positive
  # -1 is negative
  # 0 is no rating
  rating: int = 0


@me.stateclass
class State:
  backend: str = DEFAULT_AI_BACKEND
  model: Optional[str] = backends[backend].DEFAULT_MODEL
  temperature: Optional[float] = backends[backend].DEFAULT_TEMPERATURE
  max_tokens: Optional[int] = backends[backend].DEFAULT_MAX_TOKENS
  context_window: Optional[int] = OllamaAI.DEFAULT_CONTEXT_WINDOW
  batch_size: Optional[int] = OllamaAI.DEFAULT_BATCH_SIZE

  agent: Optional[str] = None
  system: Optional[str] = None
  tool: Optional[str] = None
  instruction: Optional[str] = None
  input_content_plugin: Optional[str] = None
  output_content_plugin: Optional[str] = None

  input: str
  output: list[ChatMessage]
  in_progress: bool
  sidebar_expanded: bool = False
  # Need to use dict instead of ChatMessage due to serialization bug.
  # See: https://github.com/mesop-dev/mesop/issues/659
  history: list[list[dict]]

  # snackbar
  snackbar_content: str = ""
  snackbar_is_visible: bool = False
  snackbar_duration: int = 1
  snackbar_horizontal_position: str = "center"
  snackbar_vertical_position: str = "end"

def respond_to_chat(input: str, history: list[ChatMessage]):
  global messages
  state = me.state(State)
  messages = agentmake(
    messages if messages else input,
    backend=state.backend,
    model=state.model,
    temperature=state.temperature,
    max_tokens=state.max_tokens,
    context_window=state.context_window,
    batch_size=state.batch_size,
    agent=state.agent,
    tool=state.tool,
    system=state.system,
    instruction=state.instruction,
    input_content_plugin=state.input_content_plugin,
    output_content_plugin=state.output_content_plugin,
    follow_up_prompt=input if messages else None,
    print_on_terminal=DEVELOPER_MODE,
  )
  yield markdown.markdown(messages[-1].get("content", ""))

def on_load(e: me.LoadEvent):
  me.set_theme_mode("system")

@me.page(
  security_policy=me.SecurityPolicy(
    allowed_iframe_parents=["https://mesop-dev.github.io"]
  ),
  title="AgentMake AI Studio",
  #path="/studio",
  on_load=on_load,
)
def page():
  state = me.state(State)

  snackbar(
    label=state.snackbar_content,
    action_label="Copied!",
    on_click_action=on_click_snackbar_close,
    is_visible=state.snackbar_is_visible,
    horizontal_position=state.snackbar_horizontal_position,
    vertical_position=state.snackbar_vertical_position,
  )

  with me.box(
    style=me.Style(
      background=me.theme_var("surface-container-lowest"),
      display="flex",
      flex_direction="column",
      height="100%",
    )
  ):
    with me.box(
      style=me.Style(
        display="flex", flex_direction="row", flex_grow=1, overflow="hidden"
      )
    ):
      with me.box(
        style=me.Style(
          background=me.theme_var("surface-container-low"),
          display="flex",
          flex_direction="column",
          flex_shrink=0,
          position="absolute"
          if state.sidebar_expanded and _is_mobile()
          else None,
          height="100%" if state.sidebar_expanded and _is_mobile() else None,
          width=300 if state.sidebar_expanded else None,
          z_index=2000,
        )
      ):
        sidebar()

      with me.box(
        style=me.Style(
          display="flex",
          flex_direction="column",
          flex_grow=1,
          padding=me.Padding(left=60)
          if state.sidebar_expanded and _is_mobile()
          else None,
        )
      ):
        header()
        with me.box(style=me.Style(flex_grow=1, overflow_y="scroll")):
          if state.output:
            chat_pane()
          else:
            examples_pane()
        chat_input()


def sidebar():
  global backends
  state = me.state(State)
  with me.box(
    style=me.Style(
      display="flex",
      flex_direction="column",
      flex_grow=1,
    )
  ):
    with me.box(style=me.Style(display="flex", gap=20)):
      menu_icon(icon="menu", tooltip="Menu", on_click=on_click_menu_icon)
      if state.sidebar_expanded:
        me.text(
          _APP_TITLE,
          style=me.Style(margin=me.Margin(bottom=0, top=14)),
          type="headline-6",
        )

    if state.sidebar_expanded:
      menu_item(icon="add", label="New chat", on_click=on_click_new_chat)

      me.select(
        options=[me.SelectOption(label=i, value=i) for i in SUPPORTED_AI_BACKENDS],
        label="Backend",
        style=_STYLE_INPUT_WIDTH,
        on_selection_change=on_backend_select,
        value=state.backend,
      )

      if not state.backend == "llamacpp":
        me.input(
          label="Model",
          style=_STYLE_INPUT_WIDTH,
          value=state.model if state.model else "",
          on_input=on_input_model,
        )

      me.input(
        label="Temperature",
        style=_STYLE_INPUT_WIDTH,
        value=str(state.temperature),
        on_input=on_input_temperature,
      )
      me.input(
        label="Output Token Limit",
        style=_STYLE_INPUT_WIDTH,
        value=str(state.max_tokens),
        on_input=on_input_max_tokens,
      )

      if state.backend == "ollama":
        me.input(
          label="Context Window Size",
          style=_STYLE_INPUT_WIDTH,
          value=str(state.context_window),
          on_input=on_input_context_window,
        )
        me.input(
          label="Batch Size",
          style=_STYLE_INPUT_WIDTH,
          value=str(state.batch_size),
          on_input=on_input_batch_size,
        )

      me.select(
        options=[me.SelectOption(label="[default]", value="[default]"),me.SelectOption(label="auto", value="auto")]+[me.SelectOption(label=i, value=i) for i in listResources("systems")],
        label="System",
        style=_STYLE_INPUT_WIDTH,
        on_selection_change=on_system_select,
        value="[default]" if not state.system else state.system,
      )
      me.select(
        options=[me.SelectOption(label="[none]", value="[none]")]+[me.SelectOption(label=i, value=i) for i in listResources("tools", ext="py")],
        label="Tool",
        style=_STYLE_INPUT_WIDTH,
        on_selection_change=on_tool_select,
        value="[none]" if not state.tool else state.tool,
      )
      me.select(
        options=[me.SelectOption(label="[none]", value="[none]")]+[me.SelectOption(label=i, value=i) for i in listResources("instructions")],
        label="Predefined Instruction",
        style=_STYLE_INPUT_WIDTH,
        on_selection_change=on_instruction_select,
        value="[none]" if not state.instruction else state.instruction,
      )
      me.select(
        options=[me.SelectOption(label="[none]", value="[none]")]+[me.SelectOption(label=i, value=i) for i in listResources("plugins", ext="py")],
        label="Input Content Plugin",
        style=_STYLE_INPUT_WIDTH,
        on_selection_change=on_input_content_plugin_select,
        value="[none]" if not state.input_content_plugin else state.input_content_plugin,
      )
      me.select(
        options=[me.SelectOption(label="[none]", value="[none]")]+[me.SelectOption(label=i, value=i) for i in listResources("plugins", ext="py")],
        label="Output Content Plugin",
        style=_STYLE_INPUT_WIDTH,
        on_selection_change=on_output_content_plugin_select,
        value="[none]" if not state.output_content_plugin else state.output_content_plugin,
      )
      me.select(
        options=[me.SelectOption(label="[none]", value="[none]")]+[me.SelectOption(label=i, value=i) for i in listResources("agents", ext="py")],
        label="Agent",
        style=_STYLE_INPUT_WIDTH,
        on_selection_change=on_agent_select,
        value="[none]" if not state.agent else state.agent,
      )

    else:
      menu_icon(icon="add", tooltip="New chat", on_click=on_click_new_chat)

    if state.sidebar_expanded:
      history_pane()

def history_pane():
  state = me.state(State)
  for index, chat in enumerate(state.history):
    with me.box(
      key=f"chat-{index}",
      on_click=on_click_history,
      style=me.Style(
        background=me.theme_var("surface-container"),
        border=me.Border.all(
          me.BorderSide(
            width=1, color=me.theme_var("outline-variant"), style="solid"
          )
        ),
        border_radius=5,
        cursor="pointer",
        margin=me.Margin.symmetric(horizontal=10, vertical=10),
        padding=me.Padding.all(10),
        text_overflow="ellipsis",
      ),
    ):
      me.text(_truncate_text(chat[0]["content"]))

def header():
  state = me.state(State)
  with me.box(
    style=me.Style(
      align_items="center",
      background=me.theme_var("surface-container-lowest"),
      display="flex",
      gap=5,
      justify_content="space-between",
      padding=me.Padding.symmetric(horizontal=20, vertical=10),
    )
  ):
    with me.box(style=me.Style(display="flex", gap=5)):
      if not state.sidebar_expanded:
        me.text(
          _APP_TITLE,
          style=me.Style(margin=me.Margin(bottom=0)),
          type="headline-6",
        )

    with me.box(style=me.Style(display="flex", gap=5)):
      icon_button(
        key="",
        icon="dark_mode" if me.theme_brightness() == "light" else "light_mode",
        tooltip="Dark mode"
        if me.theme_brightness() == "light"
        else "Light mode",
        on_click=on_click_theme_brightness,
      )

def examples_pane():
  with me.box(
    style=me.Style(
      margin=me.Margin.symmetric(horizontal="auto"),
      padding=me.Padding.all(15),
      width=f"min({_CHAT_MAX_WIDTH}, 100%)",
    )
  ):
    with me.box(style=me.Style(margin=me.Margin(top=25), font_size=24)):
      me.text(_EMPTY_CHAT_MESSAGE)

    with me.box(
      style=me.Style(
        display="flex",
        flex_direction="column" if _is_mobile() else "row",
        gap=20,
        margin=me.Margin(top=25),
      )
    ):
      for index, query in enumerate(_EXAMPLE_USER_QUERIES):
        with me.box(
          key=f"query-{index}",
          on_click=on_click_example_user_query,
          style=me.Style(
            background=me.theme_var("surface-container-highest"),
            border_radius=15,
            padding=me.Padding.all(20),
            cursor="pointer",
          ),
        ):
          me.text(query)

def chat_pane():
  state = me.state(State)
  with me.box(
    style=me.Style(
      background=me.theme_var("surface-container-lowest"),
      color=me.theme_var("on-surface"),
      display="flex",
      flex_direction="column",
      margin=me.Margin.symmetric(horizontal="auto"),
      padding=me.Padding.all(15),
      width=f"min({_CHAT_MAX_WIDTH}, 100%)",
    )
  ):
    for index, msg in enumerate(state.output):
      if msg.role == "user":
        user_message(message=msg)
      else:
        bot_message(message_index=index, message=msg)

    if state.in_progress:
      with me.box(key="scroll-to", style=me.Style(height=250)):
        pass

def user_message(*, message: ChatMessage):
  with me.box(
    style=me.Style(
      display="flex",
      gap=15,
      justify_content="end",
      margin=me.Margin.all(20),
    )
  ):
    with me.box(
      style=me.Style(
        background=me.theme_var("surface-container-low"),
        border_radius=10,
        color=me.theme_var("on-surface-variant"),
        padding=me.Padding.symmetric(vertical=0, horizontal=10),
        width="66%",
      )
    ):
      me.markdown(message.content)

def bot_message(*, message_index: int, message: ChatMessage):
  with me.box(style=me.Style(display="flex", gap=15, margin=me.Margin.all(20))):
    text_avatar(
      background=me.theme_var("primary"),
      color=me.theme_var("on-primary"),
      label=_BOT_AVATAR_LETTER,
    )
    # Bot message response
    with me.box(style=me.Style(display="flex", flex_direction="column")):
      me.markdown(
        message.content,
        style=me.Style(color=me.theme_var("on-surface")),
      )
      # Actions panel
      with me.box():
        #https://fonts.google.com/icons
        icon_button(
          key=f"content_copy-{message_index}",
          icon="content_copy",
          is_selected=message.rating == 1,
          tooltip="Copy",
          on_click=on_click_content_copy,
        )

def chat_input():
  state = me.state(State)
  with me.box(
    style=me.Style(
      background=me.theme_var("surface-container")
      if _is_mobile()
      else me.theme_var("surface-container"),
      border_radius=16,
      display="flex",
      margin=me.Margin.symmetric(horizontal="auto", vertical=15),
      padding=me.Padding.all(8),
      width=f"min({_CHAT_MAX_WIDTH}, 90%)",
    )
  ):
    with me.box(
      style=me.Style(
        flex_grow=1,
      )
    ):
      me.native_textarea(
        autosize=True,
        key="chat_input",
        min_rows=4,
        on_blur=on_chat_input,
        shortcuts={
          me.Shortcut(shift=True, key="Enter"): on_submit_chat_msg,
        },
        placeholder="Enter your prompt",
        style=me.Style(
          background=me.theme_var("surface-container")
          if _is_mobile()
          else me.theme_var("surface-container"),
          border=me.Border.all(
            me.BorderSide(style="none"),
          ),
          color=me.theme_var("on-surface-variant"),
          outline="none",
          overflow_y="auto",
          padding=me.Padding(top=16, left=16),
          width="100%",
        ),
        value=state.input,
      )
    with me.content_button(
      disabled=state.in_progress,
      on_click=on_click_submit_chat_msg,
      type="icon",
    ):
      me.icon("send")

@me.component
def text_avatar(*, label: str, background: str, color: str):
  me.text(
    label,
    style=me.Style(
      background=background,
      border_radius="50%",
      color=color,
      font_size=20,
      height=40,
      line_height="1",
      margin=me.Margin(top=16),
      padding=me.Padding(top=10),
      text_align="center",
      width="40px",
    ),
  )

@me.component
def icon_button(
  *,
  icon: str,
  tooltip: str,
  key: str = "",
  is_selected: bool = False,
  on_click: Callable | None = None,
):
  selected_style = me.Style(
    background=me.theme_var("surface-container-low"),
    color=me.theme_var("on-surface-variant"),
  )
  with me.tooltip(message=tooltip):
    with me.content_button(
      type="icon",
      key=key,
      on_click=on_click,
      style=selected_style if is_selected else None,
    ):
      me.icon(icon)

@me.component
def menu_icon(
  *, icon: str, tooltip: str, key: str = "", on_click: Callable | None = None
):
  with me.tooltip(message=tooltip):
    with me.content_button(
      key=key,
      on_click=on_click,
      style=me.Style(margin=me.Margin.all(10)),
      type="icon",
    ):
      me.icon(icon)

@me.component
def menu_item(
  *, icon: str, label: str, key: str = "", on_click: Callable | None = None
):
  with me.box(on_click=on_click):
    with me.box(
      style=me.Style(
        background=me.theme_var("surface-container-high"),
        border_radius=20,
        cursor="pointer",
        display="inline-flex",
        gap=10,
        line_height=1,
        margin=me.Margin.all(10),
        padding=me.Padding(top=10, left=10, right=20, bottom=10),
      ),
    ):
      me.icon(icon)
      me.text(label, style=me.Style(height=24, line_height="24px"))

# Event Handlers

def on_system_select(e: me.SelectSelectionChangeEvent):
  """Event to select system."""
  state = me.state(State)
  state.system = None if e.value == "[default]" else e.value

def on_tool_select(e: me.SelectSelectionChangeEvent):
  """Event to select tool."""
  state = me.state(State)
  state.tool = None if e.value == "[none]" else e.value

def on_instruction_select(e: me.SelectSelectionChangeEvent):
  """Event to select predefined instruction."""
  state = me.state(State)
  state.instruction = None if e.value == "[none]" else e.value

def on_input_content_plugin_select(e: me.SelectSelectionChangeEvent):
  """Event to select input content plugin."""
  state = me.state(State)
  state.input_content_plugin = None if e.value == "[none]" else e.value

def on_output_content_plugin_select(e: me.SelectSelectionChangeEvent):
  """Event to select output content plugin."""
  state = me.state(State)
  state.output_content_plugin = None if e.value == "[none]" else e.value

def on_agent_select(e: me.SelectSelectionChangeEvent):
  """Event to select agent."""
  state = me.state(State)
  state.agent = None if e.value == "[none]" else e.value

def on_backend_select(e: me.SelectSelectionChangeEvent):
  """Event to select backend."""
  global backends
  state = me.state(State)
  state.backend = e.value
  state.model = None if state.backend == "llamacpp" else backends[state.backend].DEFAULT_MODEL
  state.temperature = backends[state.backend].DEFAULT_TEMPERATURE
  state.max_tokens = backends[state.backend].DEFAULT_MAX_TOKENS

def on_input_model(e: me.InputEvent):
  state = me.state(State)
  state.model = str(e.value)

def on_input_temperature(e: me.InputEvent):
  """Event to adjust temperature slider value by input."""
  state = me.state(State)
  try:
    temperature = float(e.value)
    if _TEMPERATURE_MIN <= temperature <= _TEMPERATURE_MAX:
      state.temperature = temperature
  except ValueError:
    pass

def on_input_max_tokens(e: me.InputEvent):
  """Event to adjust output token limit."""
  state = me.state(State)
  try:
    max_tokens = int(e.value)
    if max_tokens == -1 or max_tokens >= _TOKEN_LIMIT_MIN:
      state.max_tokens = max_tokens
  except ValueError:
    pass

def on_input_context_window(e: me.InputEvent):
  """Event to adjust context window size."""
  state = me.state(State)
  try:
    context_window = int(e.value)
    state.context_window = context_window
  except ValueError:
    pass

def on_input_batch_size(e: me.InputEvent):
  """Event to adjust batch size."""
  state = me.state(State)
  try:
    batch_size = int(e.value)
    state.batch_size = batch_size
  except ValueError:
    pass

def on_click_example_user_query(e: me.ClickEvent):
  """Populates the user input with the example query"""
  state = me.state(State)
  _, example_index = e.key.split("-")
  state.input = _EXAMPLE_USER_QUERIES[int(example_index)]
  me.focus_component(key="chat_input")

def on_click_content_copy(e: me.ClickEvent):
  """Copy content"""
  global messages

  state = me.state(State)
  _, msg_index = e.key.split("-")
  msg_index = int(msg_index)
  #html_content = state.output[msg_index].content
  markdown_content = messages[msg_index+1].get("content", "")
  if shutil.which("termux-clipboard-set"): # Android Termux
    pipepager(markdown_content, cmd="termux-clipboard-set")
  else:
    pyperclip.copy(markdown_content)
  
  # open snackbar
  state.snackbar_content = markdown_content[:20] + " ..." if len(markdown_content) > 15 else ""
  state.snackbar_is_visible = True

  # Use yield to create a timed snackbar message.
  if state.snackbar_duration:
    yield
    time.sleep(state.snackbar_duration)
    state.snackbar_is_visible = False
    yield
  else:
    yield

def on_click_snackbar_close(e: me.ClickEvent):
  state = me.state(State)
  state.snackbar_is_visible = False

def on_click_thumb_up(e: me.ClickEvent):
  """Gives the message a positive rating"""
  state = me.state(State)
  _, msg_index = e.key.split("-")
  msg_index = int(msg_index)
  state.output[msg_index].rating = 1

def on_click_thumb_down(e: me.ClickEvent):
  """Gives the message a negative rating"""
  state = me.state(State)
  _, msg_index = e.key.split("-")
  msg_index = int(msg_index)
  state.output[msg_index].rating = -1

def on_click_new_chat(e: me.ClickEvent):
  """Resets messages."""
  global messages
  messages = []

  state = me.state(State)
  if state.output:
    state.history.insert(0, [asdict(messages) for messages in state.output])
  state.output = []
  me.focus_component(key="chat_input")

def on_click_history(e: me.ClickEvent):
  """Loads existing chat from history and saves current chat"""
  state = me.state(State)
  _, chat_index = e.key.split("-")
  chat_messages = [
    ChatMessage(**chat) for chat in state.history.pop(int(chat_index))
  ]
  if state.output:
    state.history.insert(0, [asdict(messages) for messages in state.output])
  state.output = chat_messages
  me.focus_component(key="chat_input")

def on_click_theme_brightness(e: me.ClickEvent):
  """Toggles dark mode."""
  if me.theme_brightness() == "light":
    me.set_theme_mode("dark")
  else:
    me.set_theme_mode("light")

def on_click_menu_icon(e: me.ClickEvent):
  """Expands and collapses sidebar menu."""
  state = me.state(State)
  state.sidebar_expanded = not state.sidebar_expanded

def on_chat_input(e: me.InputBlurEvent):
  """Capture chat text input on blur."""
  state = me.state(State)
  state.input = e.value

def on_click_regenerate(e: me.ClickEvent):
  """Regenerates response from an existing message"""
  state = me.state(State)
  _, msg_index = e.key.split("-")
  msg_index = int(msg_index)

  # Get the user message which is the previous message
  user_message = state.output[msg_index - 1]
  # Get bot message to be regenerated
  assistant_message = state.output[msg_index]
  assistant_message.content = ""
  state.in_progress = True
  yield

  start_time = time.time()
  # Send in the old user input and chat history to get the bot response.
  # We make sure to only pass in the chat history up to this message.
  output_message = respond_to_chat(
    user_message.content, state.output[:msg_index]
  )
  for content in output_message:
    assistant_message.content += content
    # TODO: 0.25 is an abitrary choice. In the future, consider making this adjustable.
    if (time.time() - start_time) >= 0.25:
      start_time = time.time()
      yield

  state.in_progress = False
  me.focus_component(key="chat_input")
  yield

def on_submit_chat_msg(e: me.TextareaShortcutEvent):
  state = me.state(State)
  state.input = e.value
  yield
  yield from _submit_chat_msg()

def on_click_submit_chat_msg(e: me.ClickEvent):
  yield from _submit_chat_msg()

def _submit_chat_msg():
  """Handles submitting a chat message."""
  state = me.state(State)
  if state.in_progress or not state.input:
    return
  input = state.input
  # Clear the text input.
  state.input = ""
  yield

  output = state.output
  if output is None:
    output = []
  output.append(ChatMessage(role="user", content=input))
  state.in_progress = True
  me.scroll_into_view(key="scroll-to")
  yield

  start_time = time.time()
  # Send user input and chat history to get the bot response.
  output_message = respond_to_chat(input, state.output)
  assistant_message = ChatMessage(role="bot")
  output.append(assistant_message)
  state.output = output
  for content in output_message:
    assistant_message.content += content
    # TODO: 0.25 is an abitrary choice. In the future, consider making this adjustable.
    if (time.time() - start_time) >= 0.25:
      start_time = time.time()
      yield

  state.in_progress = False
  me.focus_component(key="chat_input")
  yield

# Helpers
def _is_mobile():
  return me.viewport_size().width < _MOBILE_BREAKPOINT

def _truncate_text(text, char_limit=100):
  """Truncates text that is too long."""
  if len(text) <= char_limit:
    return text
  truncated_text = text[:char_limit].rsplit(" ", 1)[0]
  return truncated_text.rstrip(".,!?;:") + "..."

@me.component
def snackbar(
  *,
  is_visible: bool,
  label: str,
  action_label: str | None = None,
  on_click_action: Callable | None = None,
  horizontal_position: Literal["start", "center", "end"] = "center",
  vertical_position: Literal["start", "center", "end"] = "end",
):
  """Creates a snackbar.

  By default the snackbar is rendered at bottom center.

  The on_click_action should typically close the snackbar as part of its actions. If no
  click event is included, you'll need to manually hide the snackbar.

  Note that there is one issue with this snackbar example. No actions are possible when
  using "time.sleep and yield" to imitate a status message that fades away after a
  period of time.

  Args:
    is_visible: Whether the snackbar is currently visible or not.
    label: Message for the snackbar
    action_label: Optional message for the action of the snackbar
    on_click_action: Optional click event when action is triggered.
    horizontal_position: Horizontal position of the snackbar
    vertical_position: Vertical position of the snackbar
  """
  with me.box(
    style=me.Style(
      display="block" if is_visible else "none",
      height="100%",
      overflow_x="auto",
      overflow_y="auto",
      position="fixed",
      pointer_events="none",
      width="100%",
      z_index=1000,
    )
  ):
    with me.box(
      style=me.Style(
        align_items=vertical_position,
        height="100%",
        display="flex",
        justify_content=horizontal_position,
      )
    ):
      with me.box(
        style=me.Style(
          align_items="center",
          background=me.theme_var("on-surface-variant"),
          border_radius=5,
          box_shadow=(
            "0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"
          ),
          display="flex",
          font_size=14,
          justify_content="space-between",
          margin=me.Margin.all(10),
          padding=me.Padding(top=5, bottom=5, right=5, left=15)
          if action_label
          else me.Padding.all(15),
          pointer_events="auto",
          width=300,
        )
      ):
        me.text(
          label, style=me.Style(color=me.theme_var("surface-container-lowest"))
        )
        if action_label:
          me.button(
            action_label,
            on_click=on_click_action,
            style=me.Style(color=me.theme_var("primary-container")),
          )

def main():
  mesop_cli = shutil.which("mesop")
  this_file = os.path.realpath(__file__)
  os.system(f'''{mesop_cli} "{this_file}"''')

if __name__ == "__main__":
    test = main()