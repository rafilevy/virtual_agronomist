import * as React from "react"
import { Box, Button, CssBaseline, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Divider, Grid, IconButton, List, ListItem, ListItemSecondaryAction, ListItemText, makeStyles, Paper, Tab, Tabs, TextareaAutosize, TextField, Tooltip, Typography, useTheme,  } from "@material-ui/core"
import { AddCircle, Delete } from "@material-ui/icons";

const useStyles = makeStyles((theme) => ({
    keywordsContainer: {
        width: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "stretch",
    },
    searchBar: {
        padding: theme.spacing(1, 0),
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "center"
    },
    mainContainer: {

    },
    textField: {
        display: "block",
        marginTop: theme.spacing(1),
        backgroundColor: theme.palette.background.paper,
        borderColor: theme.palette.divider,
        padding: theme.spacing(1),
        color: "white",
        width: "100%"
    }

}));

type keyword = {
    key: number,
    word: string
    replacements: string[]
}

const templateData : keyword[] = [
    {key: 0, word: "Hey", replacements: ["Hi", 'Howdy', "Hello", "Bonjour", "howsit"]},
    {key: 1, word: "bye", replacements: ["cya", 'goodbye', "bye bye", "adios"]},
    {key: 2, word: "cat", replacements: ["meow", 'scratchy', "muffins", "cute"]},
    {key: 3, word: "dog", replacements: ["woofer", 'pupper', "yapper", "mlemmer"]}
]

export default function KeywordsPage() {
    const classes = useStyles();

    const [searchFieldValue, setSearchFieldValue] = React.useState("");
    const [keywords, setKeywords] = React.useState<keyword[]>(templateData);
    const [activeKeywords, setActiveKeywords] = React.useState<keyword[]>(templateData);

    const handleSearchChanged = (s : string) => {
        setSearchFieldValue(s);
        setActiveKeywords(keywords.filter((k)=>k.word.startsWith(s) || k.replacements.some((r)=>r.startsWith(s))));
    }

    const [keywordDialogueOpen, setKeywordDialogueOpen] = React.useState(false);
    const [dKeywordValue, setDKeywordValue] = React.useState("");
    const [dKeywordReplacements, setDKeywordReplacements] = React.useState("");
    const [dKeywordE, setDKeywordE] = React.useState("")

    const [keywordsUpdated, setKeywordsUpdated] = React.useState(true);
    React.useEffect(() => {
        const fetchKeywords = async () => {
            const result: { data: keyword[] } = await (await fetch("http://localhost:8000/keywords")).json();
            setKeywords(result["data"]);
            setActiveKeywords(result["data"]);
            setSearchFieldValue("")
        };
        fetchKeywords()
    }, [keywordsUpdated]);

    const handleDeleteKeyword = async (k: number) => {
        fetch(
            `localhost:8000/keywords/${k}`,
            {
                method: "DELETE"
            }
        ).then((res)=> {
            setKeywordsUpdated(!keywordsUpdated);
        });
    }

    const handleKeyWordSubmit = () => {
        const repl = dKeywordReplacements.split(",").map((s) => s.trim());
        if (dKeywordValue !== "" && repl.length > 0 ) {
            const body = JSON.stringify({
                keyword: dKeywordValue,
                replacements: repl
            });
            fetch("localhost:8000/keywords", {
                method: "POST",
                body: body
            }).then((res)=> {
                setDKeywordE("")
                setKeywordDialogueOpen(false);
            }).catch((e)=> {
                setDKeywordE(e.toString());
            })
        } else {
            setDKeywordE("Pleas provide a keyword and suitable replacements")
        }

    }

    return (
        <div>
            <CssBaseline />
            <Box className={classes.keywordsContainer}>
                <Box className={classes.searchBar}>
                    <TextField variant="outlined" label="Search" id="search-field"
                        value={searchFieldValue}
                        onChange={(ev)=>handleSearchChanged(ev.target.value)}
                    />
                    <Tooltip title="Add a keyword">
                        <IconButton onClick={()=>setKeywordDialogueOpen(true)} color="secondary">
                            <AddCircle />
                        </IconButton>
                    </Tooltip>
                </Box>
                <Box className={classes.mainContainer}>
                <Paper>
                    <List dense={true}>
                        {
                            activeKeywords.map((k, i)=> (
                                <ListItem key={k.key}>
                                    <ListItemText 
                                        primary={k.word}
                                        secondary={k.replacements.join(", ")}
                                    />
                                    <ListItemSecondaryAction>
                                        <IconButton color="secondary" edge="end" aria-label="delete"
                                            onClick={()=>handleDeleteKeyword(k.key)}
                                        >
                                            <Delete />
                                        </IconButton>
                                    </ListItemSecondaryAction>
                                </ListItem>
                            ))
                        }
                    </List>
                </Paper>
                </Box>
            </Box>
            <div>
                <Dialog
                    open={keywordDialogueOpen}
                    onClose={() => setKeywordDialogueOpen(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <DialogTitle id="alert-dialog-title">{"Add a new keyword"}</DialogTitle>
                    <DialogContent>
                        <DialogContentText id="alert-dialog-description">
                            Enter a keyword and it's alternatives below.
                        </DialogContentText>
                        <Box>
                            <TextField variant="outlined" label="Keyword" value={dKeywordValue} onChange={(e)=>setDKeywordValue(e.target.value)}/>
                            <TextareaAutosize value={dKeywordReplacements} onChange={(e)=>setDKeywordReplacements(e.target.value)} rowsMin={3} className={classes.textField} placeholder="Comma seperated list of replacement words"/>
                        </Box>
                        <Typography variant="caption" color="secondary">
                            {dKeywordE}
                        </Typography>
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleKeyWordSubmit} color="secondary" autoFocus>
                            Submit
                        </Button>
                    </DialogActions>
                </Dialog>
            </div>
        </div>
    )
}