import * as React from "react"
import { Box, CssBaseline, Divider, Grid, makeStyles, Paper, Tab, Tabs, Typography, useTheme,  } from "@material-ui/core"
import { ChartData, Line } from "react-chartjs-2";
import { defaults } from "react-chartjs-2";
import moment from 'moment';

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


type UsageData = {
    data : {[Key: string]: number}, 
    past_week: number, 
    past_month: number, 
    past_year: number
} 

export default function UsagePage() {
    const classes = useStyles();
    const theme = useTheme();
    defaults.global.defaultFontColor = theme.palette.text.primary;

    const generateGraphData : (data : {[Key: string]: number}) => Chart.ChartData = (data : {[Key: string]: number}) => {
        const currentDate = new Date();
        const query_counts: number[] = [];
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
                    month_string(
                        (startDay - i) <= 0 ? 
                            prev_month_day_off(currentDate.getMonth()) + (startDay - i) : 
                            startDay - i 
                    )
                );
                const key = moment(currentDate).add(-i, 'd').toISOString().split('T')[0];
                query_counts.push(key in data ? data[key] : 0);
            }
            return labels.reverse();
        }

        const chart_data : ChartData<Chart.ChartData> = {
            labels: generateMonthlyLabels(),
            datasets: [
                { 
                    data: query_counts.reverse(),
                    borderColor: theme.palette.primary.main,
                    pointBorderColor: theme.palette.text.primary,
                    fill: false,
                }
            ],
        };

        return chart_data;
    }
    const [graphData, setGraphData] = React.useState<Chart.ChartData | null>(null);
    const [weeklyTotal, setWeeklyTotal] = React.useState(0);
    const [monthlyTotal, setMonthlyTotal] = React.useState(0);
    const [yearlyTotal, setYearlyTotal] = React.useState(0);
    React.useEffect(()=> {
        const fetchData = async () => {
            const response : UsageData = await (await fetch("http://localhost:8000/usage/")).json();
            setWeeklyTotal(response.past_week);
            setMonthlyTotal(response.past_month);
            setYearlyTotal(response.past_year);
            setGraphData(generateGraphData(response.data));
        };
        fetchData();
    }, []);

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
                                Past 7 days: {weeklyTotal}
                            </Typography>
                            <Typography paragraph>
                                Past 30 days: {monthlyTotal}
                            </Typography>
                            <Typography paragraph style={{marginBottom: "0"}}>
                                Past year: {yearlyTotal}
                            </Typography>
                        </Box>
                    </Paper>
                </Grid>
                <Grid item xs>
                    <Paper className={classes.paper}>
                        {graphData && <Line options={{legend: {display: false}, title:{display: true, text: "Noº Queries"}}} data={graphData} width={300} height={300} />}
                    </Paper>
                </Grid>
            </Grid>
        </div>
    )
}
