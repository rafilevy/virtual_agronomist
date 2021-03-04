import * as React from "react"
import { Box, Button, CssBaseline, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Grid, IconButton, Input, InputLabel, Link, List, ListItem, ListItemSecondaryAction, ListItemText, makeStyles, Paper, Select, Tab, Tabs, Tooltip, Typography } from "@material-ui/core"
import { Delete, Label, SwapHoriz } from "@material-ui/icons";

type document = {
    index: number,
    name: string,
    type: "csv" | "text",
    is_table: boolean,
}

const useStyles = makeStyles((theme) => ({
    container: {
        display: "flex",
        flexDirection: "column",
        marginBottom: theme.spacing(5),
        alignItems: "flex-start",
    },
    title: {
        marginBottom: theme.spacing(2)
    },
    upButton: {
        marginRight: theme.spacing(1)
    },
    docList: {
        width: "100%",
        maxHeight: 400,
        overflow: "auto"
    },
    doc: {

    },
    filePicker: {
        padding: theme.spacing(1),
    }
}));
export default function DocumentsPage() {
    const classes = useStyles();

    const [documents, setDocuments] = React.useState<document[]>([]);

    const [uploadTextDocDialogueOpen, setUploadTextDocDialogueOpen] = React.useState(false);
    const [uploadTableDocDialogueOpen, setUploadTableDocDialogueOpen] = React.useState(false);
    const [removeDocDialogueOpen, setRemoveDocDialogueOpen] = React.useState(false);

    const [activeDocIndex, setActiveDocIndex] = React.useState(0);
    React.useEffect(()=> {
        const fetchDocuments = async () => {
            const results_documents : document[] = await (await fetch("http://localhost:8000/data/document/")).json();
            const results_tables : document[] = await (await fetch("http://localhost:8000/data/table/")).json();
            setDocuments(results_documents.concat(results_tables));
        };
        fetchDocuments()
    }, [documents.length===0]);

    const [selectedTextFile, setSelectedTextFile] = React.useState<File | null>(null);
    const [selectedTextFileE, setSelectedTextFileE] = React.useState("");
    const textFileUploadChosen = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) setSelectedTextFile(e.target.files.item(0));
    }
    const handleTextFileUpload = () => {
        if (selectedTextFile) {
            const formData = new FormData();
            formData.append("file", selectedTextFile);
            fetch(
                'http://localhost:8000/data/document/',
                {
                    method: 'POST',
                    body: formData,
                }
            ).then((res)=> {
                setDocuments([]);
                setUploadTextDocDialogueOpen(false);
            }).catch((e)=> {
                console.error(e);
                setSelectedTextFileE("There was a problem uploading the file.")
            })
            setSelectedTextFileE("");
        } else {
            setSelectedTextFileE("You must choose a file to upload");
        }
    }

    const [selectedTableFile, setSelectedTableFile] = React.useState<File | null>(null);
    const [selectedTableFileE, setSelectedTableFileE] = React.useState("");
    const tableFileUploadChosen = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) setSelectedTableFile(e.target.files.item(0));
    }
    const handleTableFileUpload = () => {
        if (selectedTextFile !== null && selectedTableFile !== null) {
            const formData = new FormData();
            formData.append("txt", selectedTextFile);
            formData.append("csv", selectedTableFile);
            fetch(
                'http://localhost:8000/data/table/',
                {
                    method: 'POST',
                    body: formData,
                }
            ).then((res)=> {
                setDocuments([]);
                setUploadTableDocDialogueOpen(false);
            }).catch((e)=> {
                console.error(e);
                setSelectedTableFileE("There was a problem uploading the file.")
            })
            setSelectedTableFileE("");
        } else {
            setSelectedTableFileE("You must choose a suitable csv file and text descriptor to upload");
        }
    }

    const handleRemoveButtonClicked = (i: number) => {
        setActiveDocIndex(i);
        setRemoveDocDialogueOpen(true);
    }
    const handleDocumentRemove = (i: number) => {
        var path = documents[i].is_table ? 'table' : 'document'
        fetch(`http://localhost:8000/data/${path}/${documents[i].index}/`, 
            {
                method: "DELETE"
            }
        );
        setDocuments([]);
        setRemoveDocDialogueOpen(false);
    }
    const trainerHelper = async (extra={}) => {
        await (await fetch(`http://localhost:8000/data/reload/`, extra)).json();
    };

    return (
        <div>
            <CssBaseline />
                <Box>
                    <Box className={classes.container}>
                        <Typography className={classes.title} variant="h4">
                            Upload a new document
                        </Typography>
                        <Box>
                        <Button className={classes.upButton} variant="contained" onClick={()=>setUploadTextDocDialogueOpen(true)}>
                            Text document
                        </Button>
                        <Button className={classes.upButton} variant="contained" onClick={()=>setUploadTableDocDialogueOpen(true)}>
                            Table Document
                        </Button>
                        </Box>
                    </Box>
                    <Box className={classes.container}>
                        <Typography variant="h4">
                            Existing documents
                        </Typography>
                        <Paper className={classes.docList}>
                            <List component="ul">
                                {documents.map((doc, i)=>
                                    <ListItem className={classes.doc} key={i} button>
                                        <ListItemText
                                            primary={doc.name}
                                        />
                                        <ListItemSecondaryAction>
                                            <Tooltip title="Remove document">
                                                <IconButton color="secondary" edge="end"
                                                    onClick = {()=>handleRemoveButtonClicked(i)}
                                                >
                                                    <Delete />
                                                </IconButton>
                                            </Tooltip>
                                        </ListItemSecondaryAction>
                                    </ListItem>
                                )}
                            </List>
                        </Paper>
                    </Box>
                    <Box mt="5px">
                        <Button variant="contained" color="secondary"
                            onClick={()=>trainerHelper({
                                method: "POST"
                            })}
                        >
                            Reload Document Store
                        </Button>
                    </Box>
                </Box>
            <div>
                <Dialog id="upload-text-doc-dialogue"
                    open={uploadTextDocDialogueOpen}
                    onClose={()=>setUploadTextDocDialogueOpen(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <DialogTitle id="alert-dialog-title">{"Upload a new text document"}</DialogTitle>
                    <DialogContent>
                        <Box>
                            <DialogContentText id="alert-dialog-description">
                                Choose a file to upload
                            </DialogContentText>
                            <Box>
                                <input accept=".txt" type="file" name="chosenFile" onChange={textFileUploadChosen} />
                            </Box>
                            {   selectedTextFileE !== "" &&
                                <Typography variant="caption" color="secondary">{selectedTextFileE}</Typography>
                            }
                        </Box>
                    </DialogContent>
                    <DialogActions>
                    <Button onClick={()=>handleTextFileUpload()} color="primary" autoFocus>
                        Upload
                    </Button>
                    </DialogActions>
                </Dialog>
                <Dialog id="upload-csv-doc-dialogue"
                    open={uploadTableDocDialogueOpen}
                    onClose={()=>setUploadTableDocDialogueOpen(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <DialogTitle id="alert-dialog-title">{"Upload a new table document"}</DialogTitle>
                    <DialogContent>
                        <Box>
                            <DialogContentText id="alert-dialog-description">
                                Choose a csv file and accompanying text descriptor file for it
                            </DialogContentText>
                            <Box>
                                <Box>
                                    CSV File:
                                    <input className={classes.filePicker} accept=".csv" type="file" name="csvFile" onChange={tableFileUploadChosen} />
                                </Box>
                                <Box>
                                    Text File:
                                    <input className={classes.filePicker} accept=".txt" type="file" name="textFile" onChange={textFileUploadChosen} />
                                </Box>
                                {   selectedTableFileE !== "" &&
                                    <Typography variant="caption" color="secondary">{selectedTableFileE}</Typography>
                                }
                            </Box>
                            <Typography variant="caption"></Typography>
                        </Box>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleTableFileUpload} color="secondary" autoFocus>
                            Upload
                        </Button>
                    </DialogActions>
                </Dialog>
                <Dialog id="remove-doc-dialogue"
                    open={removeDocDialogueOpen}
                    onClose={()=>setRemoveDocDialogueOpen(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <DialogTitle id="alert-dialog-title">{"Remove document"}</DialogTitle>
                    <DialogContent>
                        <DialogContentText id="alert-dialog-description">
                            Are you sure you wish to delete the document? This action cannot be undone.
                        </DialogContentText>
                    </DialogContent>
                    <DialogActions>
                    <Button onClick={()=>handleDocumentRemove(activeDocIndex)} color="secondary" autoFocus>
                        Delete
                    </Button>
                    </DialogActions>
                </Dialog>
            </div>
        </div>
    )
}