import * as React from "react"
import { Divider, IconButton, makeStyles, Paper, Typography } from "@material-ui/core"
import { message } from "./message"
import { CheckCircleOutlineSharp, ReportSharp } from "@material-ui/icons";
import { green } from '@material-ui/core/colors';

const useStyles = makeStyles({
    container: {
        padding: "10px",
        margin: "20px",
    },
    msg_left: {
        marginRight: "60px"
    },
    msg_right: {
        marginLeft: "60px"
    },
    message: {
        display: "flex",
        alignItems: "stretch",
    },
    innerMessage: {
        flexGrow: 1,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
    },
    separator: {
        alignSelf: "flex-start",
    },
    messageText: {
        width: "100%",
        height: "auto",
        textAlign: "left",
        margin: "10px 0px",
    }
});

export default function MultiMessage({msg, onChosenOption} : {msg: message, onChosenOption: (n: number) => void}) {
    const classes = useStyles();
    const [chosenOption, _setChosenOption] = React.useState<number>();
    const setChosenOption = (i: number) => { _setChosenOption(i); onChosenOption(i) }

    return (
        <Paper className={[classes.container, msg.from ? classes.msg_left : classes.msg_right].join(" ")}>
                <Typography variant="caption">
                    {msg.from ? "Virtual Agronomist" : "You"} - {msg.time.toLocaleTimeString().substr(0,5)} - {"please select the best response"}
                </Typography>
                {msg.options!.map((text, i) => 
                    <>
                        {i != 0 && <Divider className={classes.separator} />}
                        <div className={classes.message}>
                            <div className={classes.innerMessage}>
                                <Typography variant="body1" className={classes.messageText}>
                                    {text}
                                </Typography>
                            </div>
                            <div style={{
                                alignSelf: "stretch",
                                display: "flex",
                                justifyContent: "center",
                                alignItems: "center",
                            }}>
                                <IconButton aria-label="correct" onClick={() => chosenOption == undefined && (setChosenOption(i)) }>
                                    <CheckCircleOutlineSharp style={{ color: chosenOption == i ? green[500] : green[100] }} />
                                </IconButton>
                            </div>
                        </div>
                    </>
                )}
        </Paper>
    )
}