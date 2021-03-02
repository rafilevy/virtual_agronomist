import * as React from "react"
import { Box, CssBaseline, Divider, Grid, makeStyles, Paper, Tab, Tabs, Typography, useTheme,  } from "@material-ui/core"
import { ChartData, Line } from "react-chartjs-2";
import { defaults } from "react-chartjs-2";
import { TabPanel } from "../utils/TabPanel";

const MONTH_MS = 1000*60*60*24*30
const WEEK_MS = 1000*60*60*24*7
const DAY_MS = 1000*60*60*24

const useStyles = makeStyles((theme) => ({
    paper: {
        padding: theme.spacing(2),
    },
    paperTitle: {
        textAlign: "center"
    },
    paperText: {
        paddingTop: theme.spacing(2),
    }
}));


type UsagePageProps = {
    queries: number[] //Date numbers (millisecond since midnight January 1, 1970 UTC)
}

export default function UsagePage(props: UsagePageProps) {
    const classes = useStyles();
    const theme = useTheme();
    defaults.global.defaultFontColor = theme.palette.text.primary;

    const generateGraphData : (type: "DAILY" | "MONTHLY") => [Chart.ChartData, number] = (type : "DAILY" | "MONTHLY") => {
        const currentDate = new Date();
        const cuttofDate = 
            (new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate())).valueOf() -
            (DAY_MS * (type==="DAILY" ? 7 : 30));

        const query_counts : number[] = [];
        let prev = null;
        let i = -1;
        let total_queries = 0;
        for (let t of props.queries) {
            const rounded = t - (t % DAY_MS);
            if (rounded < cuttofDate) break;
            if (rounded === prev) {
                query_counts[i]++;
            } else {
                i++;
                prev = rounded;
                query_counts[i] = 1;
            }
            total_queries++;
        }
        
        const generateDailyLabels = () => {
            const startDay = currentDate.getDay();
            const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
            return weekdays.slice(startDay, weekdays.length).concat(weekdays.slice(0, startDay));
        };
        const generateMonthlyLabels = () => {
            const startDay = currentDate.getDate();
            const labels = [];
            const prev_month_day_off = (month : number) => {
                if ([0, 1, 3, 5, 7, 8, 10].includes(month)) return 31;
                if ([4,6,9,11].includes(month)) return 30;
                const year = currentDate.getFullYear();
                const leap = (year % 4 === 0) && (year % 100 != 0 || year % 400 == 0);
                return leap ? 29 : 28;
            }
            const month_string = (month: number) => {
                let u = month % 10;
                if (u === 1) return `${month}st`;
                if (u === 2) return `${month}nd`;
                if (u === 3) return `${month}rd`;
                return`${month}th`;
            }
            for (let i = 0; i<30; i++) {
                labels.push(
                    month_string((startDay - i) <= 0 ? prev_month_day_off(currentDate.getMonth()) + (startDay - i) : startDay - i ));
            }
            return labels.reverse();
        }

        const chart_data : ChartData<Chart.ChartData> = {
            labels: type==="DAILY" ? generateDailyLabels() : generateMonthlyLabels(),
            datasets: [
                { 
                    data: query_counts.reverse(),
                    borderColor: theme.palette.primary.main,
                    pointBorderColor: theme.palette.text.primary,
                    fill: false,
                }
            ],
        };

        return [chart_data, total_queries];
    }

    const [daily_graph_data, weekly_total] = generateGraphData("DAILY");
    const [monthly_graph_data, monthly_total] = generateGraphData("MONTHLY");

    const [graphTabValue, setGraphTabValue] = React.useState(0);
    const handleGraphTabChange = (_ : any, newVal : number) => setGraphTabValue(newVal);

    return (
        <div>
            <CssBaseline />
            <Grid container spacing={2}>
                <Grid item xs>
                    <Paper className={classes.paper}>
                        <Typography variant="h2" className={classes.paperTitle}>Total Queries</Typography>
                        <Divider></Divider>
                        <Box className={classes.paperText}>
                            <Typography paragraph>
                                Past 7 days: {weekly_total}
                            </Typography>
                            <Typography paragraph>
                                Past 30 days: {monthly_total}
                            </Typography>
                            <Typography paragraph style={{marginBottom: "0"}}>
                                Past year: {props.queries.length}
                            </Typography>
                        </Box>
                    </Paper>
                </Grid>
                <Grid item xs>
                    <Paper className={classes.paper}>
                        <Tabs 
                            value={graphTabValue} 
                            onChange={handleGraphTabChange}
                            indicatorColor="primary"
                            textColor="primary"
                        >
                            <Tab label="7 Days"/>
                            <Tab label="30 Days"/>
                        </Tabs>
                        <TabPanel value={graphTabValue} index={0}>
                            <Line options={{legend: {display: false}, title:{display: true, text: "Noº Queries"}}} data={daily_graph_data} width={300} height={300} />
                        </TabPanel>
                        <TabPanel value={graphTabValue} index={1}>
                            <Line options={{legend: {display: false}, title:{display: true, text: "Noº Queries"}}} data={monthly_graph_data} width={300} height={300} />
                        </TabPanel>
                    </Paper>
                </Grid>
            </Grid>
        </div>
    )
}