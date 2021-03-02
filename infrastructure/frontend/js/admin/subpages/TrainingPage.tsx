import * as React from "react"
import { Box, Button, CssBaseline, DialogActions, DialogTitle, Divider, Grid, List, ListItem, ListItemText, makeStyles, Paper, Tab, Tabs, Tooltip, Typography, useTheme,  } from "@material-ui/core"
import { Dialog } from "@material-ui/core";
import { DialogContentText } from "@material-ui/core";
import { DialogContent } from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
    paper: {
        padding: theme.spacing(2),
    },
    section: {
        width:"100%"
    },
    qaContainer: {
        marginTop: theme.spacing(1),
        padding: theme.spacing(2),
        width: "100%"
    },
    question: {
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "center"
    },
    answersContainer: {

    },
    answer: {
        fontSize: "0.8rem",
        padding: "3px 10px",
    },
    correctAnswer: {
        backgroundColor: theme.palette.success.main,
        "&:hover": {
            backgroundColor: theme.palette.success.dark
        }
    }
}));


type TrainingPageProps = {
   
}

type feedbackQuestion = {
    question: string,
    options: string[],
    choice: number,
    key: number
}

export default function TrainingPage(props: TrainingPageProps) {
    const classes = useStyles();
    const theme = useTheme();

    const [feedbackQuestions, setFeedbackQuestions] = React.useState<feedbackQuestion[]>([]);
    const [trainingSetRound, setTrainingSetRound] = React.useState<number>();
    const [trainingSetCount, setTrainingSetCount] = React.useState<number>();
    const [isTraining, setIsTraining] = React.useState<boolean>();


    const trainerHelper = async (url: string, extra={}) => {
        const result : {count: number, round: number, training: boolean} = await (await fetch(`http://localhost:8000/${url}/`, extra)).json();
        console.log(result);
        setTrainingSetCount(result["count"]);
        setTrainingSetRound(result["round"]);
        setIsTraining(result["training"]);
    };

    React.useEffect(()=> {
        const fetchQuestions = async () => {
            const result : {data: feedbackQuestion[]} = await (await fetch("http://localhost:8000/feedback/")).json();
            setFeedbackQuestions(result["data"]);
        };
        fetchQuestions()
    }, [feedbackQuestions.length===0]);
    
    React.useEffect(()=> {
        trainerHelper("train");
    }, []);

    const deleteFeedbackQuestion = async (key: number) => {
        trainerHelper("feedback", {
            method: "DELETE",
            body: key.toString()
        });
        setFeedbackQuestions(feedbackQuestions.slice(1, feedbackQuestions.length));
    }

    const submitFeedbackQuestion = async (key: number, choice: number) => {
        const body = JSON.stringify({key, choice});
        trainerHelper("feedback", {
            method: "POST",
            body: body,
            headers: [["Content-Type", "application/json"]]
        });
        setFeedbackQuestions(feedbackQuestions.slice(1, feedbackQuestions.length));
    }

    const [commitDialogueOpen, setCommitDialogueOpen] = React.useState(false);
    const handleTrainingCommit = () => {
        trainerHelper("train", {
            method: "POST"
        });
        setCommitDialogueOpen(false);
    }

    return (
        <div>
            <CssBaseline />
            <Grid container spacing={4}>
                <Grid item xl>
                    <Paper className={classes.paper}>
                        <Typography>
                            On this page you will find various resources to help fine tune the ML model behind the virtual agronomist.
                            Training will not take effect immediately, instead all data is batched and can then be batched to run the system.
                            At the bottom of this page the commit training section allows this to be done. Hover over the sections to find out more.
                        </Typography>
                    </Paper>
                </Grid>
                <Grid item xl className={classes.section}>
                    <Tooltip title="You will be shown a list of questions asked by users which were flagged as being incorrect. Choose the the best option from the list of answers given below. The answer the user chose is highlited in green.">
                        <Typography variant="h2">
                            Question answer review
                        </Typography>
                    </Tooltip>
                    <Divider />
                    <Paper className={classes.qaContainer}>
                        {
                            feedbackQuestions.length === 0 ? 
                            <Typography variant="h5" color="textSecondary">
                                There are no question answer pairs to train on at the moment. Try again later.
                            </Typography>
                            :
                            <div>
                                <Box className={classes.question}>
                                    <Typography variant="h5" color="textSecondary">
                                        Question: {feedbackQuestions[0].question}
                                    </Typography>
                                    <Button variant="contained" onClick={()=>deleteFeedbackQuestion(feedbackQuestions[0].key)}>
                                        Skip
                                    </Button>
                                    </Box>
                                <Box className={classes.answersContainer}>
                                    <List component="ul">
                                        {feedbackQuestions[0].options.map((answer, i)=>
                                            <ListItem className={`${classes.answer} ${feedbackQuestions[0].choice === i ? classes.correctAnswer : ""}`} key={i} onClick={()=>submitFeedbackQuestion(feedbackQuestions[0].key, i)} button>
                                                <ListItemText
                                                    primary={answer}
                                                />
                                            </ListItem>
                                        )}
                                    </List>
                                </Box>
                            </div>
                        }
                    </Paper>
                </Grid>
                {isTraining ? <Grid item xl className={classes.section}>
                <Typography variant="h5">
                        training...
                    </Typography>
                </Grid> : <Grid item xl className={classes.section}>
                    <Typography variant="h3">
                        Commit training round: {trainingSetRound}
                    </Typography>
                    <Divider />
                    <Box mt="5px">
                        <Button variant="contained" color="secondary"
                            onClick={()=>setCommitDialogueOpen(true)}
                        >
                            Commit Set (#{trainingSetCount})
                        </Button>
                    </Box>
                </Grid>}
            </Grid>
            <div>
                <Dialog
                    open={commitDialogueOpen}
                    onClose={()=>setCommitDialogueOpen(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <DialogTitle id="alert-dialog-title">{"Commit Training Data"}</DialogTitle>
                    <DialogContent>
                    <DialogContentText id="alert-dialog-description">
                        Proceeding will send the training data to the model. This action cannot be undone. Are you sure you want to proceed?
                    </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                    <Button onClick={handleTrainingCommit} color="secondary" autoFocus>
                        Agree
                    </Button>
                    </DialogActions>
                </Dialog>
            </div>
        </div>
    )
}