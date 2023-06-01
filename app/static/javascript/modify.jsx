class Edit extends React.Component{
    state = {
        submit: false,
        edit: true
    };

    turnInput = (rows,sub) => {
        this.setState({edit: false});
        rows[1].childNodes[0].nodeValue = ""
        rows[2].childNodes[0].nodeValue = ""
        rows[3].childNodes[0].nodeValue = ""
        rows[4].childNodes[0].nodeValue = ""
        rows[5].childNodes[0].nodeValue = ""
        rows[1].children[0].type = "email"
        rows[2].children[0].type = "text"
        rows[3].children[0].type = "text"
        rows[4].children[0].type = "text"
        rows[5].children[0].type = "text"
        
        // rows[3].innerHTML = "<input type='text' placeHolder = 'Doe' name='last'> </input>"
        // rows[4].innerHTML = "<input type='text' placeHolder = 'City, State' name='location'> </input>"
        // rows[5].innerHTML = "<input type='text' placeHolder = '$0.0' name='balance'> </input>"
        sub.hidden = ""
        
        console.log(rows[2].childNodes);
    }

    render() {
        let rows = document.getElementById("user-info").children;
        let sub = document.getElementById("submit-btn")
        
        const editBtn = (
                    <React.Fragment>
                            <button type="button" className="btn btn-warning" onClick={()=>this.turnInput(rows,sub)}> 
                            <i className="bi bi-pencil"></i> Edit
                            </button> 
                    </React.Fragment>);
        
        const submitBtn = (
            <React.Fragment>
                    <button type="submit" className="btn btn-success" onClick={()=>this.turnInput(rows)}> 
                        <i class="bi bi-check-circle"></i> Submit
                    </button>
            </React.Fragment>);

        if (!this.state.submit){
            return this.state.edit ? editBtn : None}
    }
}

ReactDOM.render( <Edit/>,document.getElementById("edit-btn"))