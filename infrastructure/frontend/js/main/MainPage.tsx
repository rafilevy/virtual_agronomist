import * as React from "react"
import { Box, Button, Container, IconButton, makeStyles, Paper, TextareaAutosize, Typography } from "@material-ui/core"
import SendIcon from "@material-ui/icons/Send"
import ChatMessage from "./ChatMessage"
import { message } from "./message";
import useWebSocket from 'react-use-websocket';
import StatusMessage from "./StatusMessage";
import MultiMessage from "./MultiMessage";

const useStyles = makeStyles((theme)=> ({
    root: {
        width: "100%",
        height: "100%",
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-evenly"
    },
    messages: {
        backgroundColor: theme.palette.grey[300],
        flex: "1",
        overflowY: "auto",
    },
    input: {
        backgroundColor: theme.palette.grey[300],
        display: "flex",
        flexDirection: "row",
        alignItems: "center",
        marginTop: "10px",
        padding: "10px",
    },
    text_input: {
        width: "100%",
        padding: "10px 10px",
        boxSizing: "border-box",
        border: `2px solid ${theme.palette.primary.light}`,
        borderRadius: theme.shape.borderRadius,
        backgroundColor: theme.palette.grey[300],
        resize: "none",
        fontSize: "1.2em",
        fontFamily: theme.typography.fontFamily,
        "&:focus": {
            outline: "none",
            border: `2px solid ${theme.palette.primary.main}`,
            borderRadius: theme.shape.borderRadius
        }
    }
}));

const ws_scheme = window.location.protocol == 'https:' ? 'wss' : 'ws';
const socketUrl = `${ws_scheme}://${location.host}/ws/chat/`;


function MainPage() {
    const classes = useStyles();
    const { sendJsonMessage, lastMessage } = useWebSocket(socketUrl);
    const inputMessage = React.useMemo(() => {
        if (lastMessage) {
            return JSON.parse(lastMessage.data);
        }
        return undefined;
    }, [lastMessage]);

    const [messages, setMessages] = React.useState<message[]>([]);
    const [questionText, setQuestionText] = React.useState("");
    const [lockInput, setLockInput] = React.useState(false);

    const messageContainer = React.useRef<HTMLDivElement>(null);
    const textArea = React.useRef<HTMLTextAreaElement>(null);

    React.useEffect(()=> {
        if (messageContainer.current)
            messageContainer.current.scrollTop = messageContainer.current.scrollHeight;
        if (textArea.current)
            textArea.current.focus();
    })

    React.useEffect(() => {
        if (inputMessage) {
            inputMessage['time'] = new Date(Date.parse(inputMessage['time']));
            console.log(inputMessage);
            setLockInput(false);
            setMessages([...messages, inputMessage]);
        }
    }, [inputMessage]);

    const captureKeyPress = (ev : React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (!ev.shiftKey && ev.key === "Enter") {
            ev.preventDefault()
            sendText();
        }
    }

    const sendText = () => {
        if (lockInput) {
            setQuestionText("");
            return;
        }
        if (questionText) {
            const msg : message = {
                from: false,
                time: new Date(),
                text: questionText
            };
            //SEND MESSAGE TO BACKEND
            sendJsonMessage(msg);
            setLockInput(true);
            setQuestionText("");
            setMessages([...messages, msg]);
        }
    };

    const sendCorrect = React.useCallback(() => {
        sendJsonMessage({ action: "correct"});
    }, [sendJsonMessage]);

    const sendReport = React.useCallback(() => {
        sendJsonMessage({ action: "report"});
    }, [sendJsonMessage]);

    const sendCorrectAnswer = React.useCallback((i: number) => {
        sendJsonMessage({ action: "answer", index: i});
    }, [sendJsonMessage]);

    return (
        <Container maxWidth="md" className={classes.root}>
            <Paper ref={messageContainer} className={classes.messages}>
                {
                    messages.map((msg: message, i: number)=> {
                        const latest = i == messages.length - 1;
                        if (msg.options) return <MultiMessage key={i} msg={msg} onChosenOption={sendCorrectAnswer} latest={latest}></MultiMessage>;
                        else if (msg.status) return <StatusMessage key={i} msg={msg}></StatusMessage>;
                        return <ChatMessage key={i} msg={msg} onReport={sendReport} onCheck={sendCorrect} latest={latest}></ChatMessage>;
                    })
                }
            </Paper>
            <Paper className={classes.input}>
                <TextareaAutosize ref={textArea} placeholder="Type here" value={questionText} onChange={(ev)=>setQuestionText(ev.target.value)} onKeyPress={captureKeyPress} rowsMin={2} rowsMax={7} className={classes.text_input}/>
                <IconButton aria-label="send" color="primary" onClick={(ev)=>sendText()}>
                    <SendIcon/>
                </IconButton>
            </Paper>
        </Container>
    )
}

export default MainPage;
