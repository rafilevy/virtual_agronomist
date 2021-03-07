import * as React from "react"
import { Box, Button, makeStyles, Paper, Typography } from "@material-ui/core"

const useStyles = makeStyles((theme) => ({
    paper: {
        padding: theme.spacing(2),
    },
    section: {
        width: "100%",
        marginBottom: theme.spacing(4)
    },
    filePicker: {
        padding: theme.spacing(1),
    }
}));

export default function ConfigUploadPage() {
    const classes = useStyles();
    const [contractions, setContractions] = React.useState<File | null>(null);
    const [pressureScore, setPressureScore] = React.useState<File | null>(null);
    const [categories, setCategories] = React.useState<File | null>(null);
    const [translation, setTranslation] = React.useState<File | null>(null);
    const [uploadHelp, setUploadHelp] = React.useState("");
    const fileUploadChosen = (setter: React.Dispatch<React.SetStateAction<File | null>>) => 
        (e: React.ChangeEvent<HTMLInputElement>) => {
            if (e.target.files) setter(e.target.files.item(0));
        }
    ;
    const upload = () => {
        if (contractions || pressureScore || categories || translation) {
            const formData = new FormData();
            contractions && formData.append("parser", contractions);
            pressureScore && formData.append("pressure_score", pressureScore);
            categories && formData.append("categories", categories);
            translation && formData.append("timing", translation);
            fetch(
                'http://localhost:8000/data/config/',
                {
                    method: 'POST',
                    body: formData,
                }
            ).then((res)=> {
                setContractions(null);
                setPressureScore(null);
                setCategories(null);
                setTranslation(null);
                setUploadHelp("Reconfigured!");
            }).catch((e)=> {
                console.error(e);
                setUploadHelp("There was a problem uploading the file.");
            })
            setUploadHelp("");
        } else {
            // allert
            setUploadHelp("Please upload at least one file.");
        }
    };

    return (
        <Box>
            <Typography variant="h5">
                Upload configuration documents.
            </Typography>
            <Box className={classes.section} mt="20px">
                <Paper className={classes.paper}>
                    <Box>
                        English Contractions for the Parser (.json):
                        <input className={classes.filePicker} accept=".json" type="file" name="csvFile" onChange={fileUploadChosen(setContractions)} />
                    </Box>
                    <Box>
                        Pressure Score Breakdown (.csv):
                        <input className={classes.filePicker} accept=".csv" type="file" name="textFile" onChange={fileUploadChosen(setPressureScore)} />
                    </Box>
                    <Box>
                        Categories to further prompt (.csv):
                        <input className={classes.filePicker} accept=".csv" type="file" name="textFile" onChange={fileUploadChosen(setCategories)} />
                    </Box>
                    <Box>
                        Timing Translation per crop (.csv):
                        <input className={classes.filePicker} accept=".csv" type="file" name="textFile" onChange={fileUploadChosen(setTranslation)} />
                    </Box>
                    {   uploadHelp !== "" &&
                        <Typography variant="caption" color="secondary">{uploadHelp}</Typography>
                    }
                </Paper>
            </Box>
            <Box mt="10px">
                <Button variant="contained" color="secondary" onClick={upload}>
                    Reconfigure
                </Button>
            </Box>
        </Box>
    );
}