<header>
    <h1>Quick Sqlite 1.0.0</h1>
    <p>It's a python library written purely in Python to do faster and better sqlite operations</p>
    <hr>
    <h2> Why Quick Sqlite? </h2>
    <ul>
        <li>No need to write such a lengthy SQL code.</li>
        <li>No need to create custom function for query.</li>
        <li>Best for lightweight and simple <b>Sqlite3</b> operations</li>
        <li>New features almost every week :)</li>
    </ul>
    <div class="contents">
        <h2>Main Contents</h2>
        <ul>
            <li><a href=""><b><i>Database()</i></b></a> Class containing methods and Sqlite operations.</li>
            <li><a href=""><b><i>create_table()</i></b></a> Function use to create table.</li>
            <li><a href=""><b><i>insert()</i></b></a> Function use to insert data.</li>
            <li><a href=""><b><i>select_all()</i></b></a> Function use to select all data from a column.</li>
            <li><a href=""><b><i>select_from()</i></b></a> Function use to select data from a single row.</li>
            <li><a href=""><b><i>update()</i></b></a> Function use to update data.</li>
            <li><a href=""><b><i>delete()</i></b></a> Function use to delet row.</li>
        </ul>
    </div>
</header>

<hr>
<div class="database">
    <h2><code><b><i>Database()</i></b></code> Class</h2>
    <p>This is the class which is responsible for database creation and all the operation under a database.</p><br>
    <code>Database(db_name)</code>
    <div class="params">
        <h3>Parameters</h3>
        <p>It takes one parameter.</p>
        <ul>
            <li><code>db_name</code> Must be endswith ".db" extension</li>
        </ul>
    </div>
    <div class="examples">
        <h3>Examples</h3>
        <p>Here is an example</p>
        <ul>
            <li><a href=""><b><i>Click here!</i></b></a></li>
        </ul>
    </div>
</div>

<hr>
<div class="create_table">
    <h2><code><b><i>Database.create_table()</i></b></code> Function</h2>
    <p>This is the function which is used to create table in database</p><br>
    <code>Database.create_table(table_name,**kwargs)</code>
    <div class="parameter">
        <h3>Parameters</h3>
        <p>It takes 1 or more parameters</p>
        <ul>
            <li><code>table_name</code> Name of the table you want to be in your database</li>
            <li>kwargs must be in the form <code>column_name = dtype</code> <b>Dtype must be valid sqlite datatype.</b>
            </li>
        </ul>
    </div>
    <div class="return">
        <h3>Return</h3>
        <p>None</p>
    </div>
    <div class="examples">
        <h3>Examples</h3>
        <p>Here is an example</p>
        <ul>
            <li><a href=""><b><i>Click here!</i></b></a></li>
        </ul>
    </div>
</div>

<div class="insert">
    <h2><code><b><i>Database.insert()</i></b></code> Function</h2>
    <p>This function is used to insert data in table.</p><br>
    <code>Database.insert(table_name,column,data_to_insert)</code>
    <div class="parameter">
        <h3>Parameters</h3>
        <p>It takes 3 parameters</p>
        <ul>
            <li><code>table_name</code> Name of the table in which you want to insert data.</li>
            <li><code>columns</code> Name of the column in which you want to insert data. <b>Must be list.</b></li>
            <li><code>data_to_insert</code>Data which you want to insert. <b>Must be list</b></li>
            <h4>Note</h4>
            <ul>
                <li><code>len(column)</code> must be equal to <code>len(data_to_insert)</code></li>
                <li><code>column[0]</code> will store the data which is at <code>data_to_insert[0]</code></li>
            </ul>
        </ul>
    </div>
    <div class="return">
        <h3>Return</h3>
        <p>None</p>
    </div>
    <div class="examples">
        <h3>Examples</h3>
        <p>Here is an exmaple.</p>
        <ul>
            <li><a href=""><b><i>Click here!</i></b></a></li>
        </ul>
    </div>
</div>

<div class="select_all">
    <h2><code><b><i>Database.select_all()</i></b></code> Function</h2>
    <p>This function is used to select all the data from a given column</p><br>
    <code>Database.select_all(table_name,column,fetch="single")</code>
    <div class="paramtere">
        <h3>Parameters</h3>
        <p>It takes 3 parameters , 2 are must and other is optional</p>
        <ul>
            <li><code>table_name</code> Name of the table from which you want to get or select data.</li>
            <li><code>column</code> Name of the column.</li>
            <li><code>fetch</code> This depend upon you if you want to <code>fetchall()</code> use "all" otherwise "single". <b>Default is "single"</b></li>
        </ul>
    </div>
    <div class="return">
        <h3>Return</h3>
        <p>Tuple</p>
    </div>
    <div class="examples">
        <h3>Examples</h3>
        <p>Here is an example.</p>
        <ul>
            <li><a href=""><b><i>Click here!</i></b></a></li>
        </ul>
    </div>
</div>


<div class="select_from">
    <h2><code><b><i>Database.select_from()</i></b></code> Function</h2>
    <p>This function is used to select data from a particular row.</p><br>
    <code>Database.select_from(table_name,column,from_where,fetch="single")</code>
    <div class="parameter">
        <h3>Parameters</h3>
        <p>It takes 4 parameter, 3 are must and other is optional</p>
        <ul>
            <li><code>table_name</code> Name of the table from which you want to get or select data.</li>
            <li><code>column</code> Name of the column.</li>
            <li><code>from_where</code> It is the list of value and a pair from where you want to get data.</li>
            <li><code>fetch</code> This depend upon you if you want to <code>fetchall()</code> use "all" otherwise "single". <b>Default is "single"</b></li>
            <h4>Note</h4>
            <ul>
                <li><code>len(from_where)</code> should be equals to 2</li>
                <li><code>from_where[0]</code> should be a column name and <code>from_where[1]</code> should be the value of that column which belongs to a row.</li>
            </ul>
        </ul>
    </div>
    <div class="return">
        <h3>Return</h3>
        <p>Tuple</p>
    </div>
    <div class="examples">
        <h3>Examples</h3>
        <p>Here is an example.</p>
        <ul>
            <li><a href=""><b><i>Click here!</i></b></a></li>
        </ul>
    </div>
</div>

<div class="update">
    <h2><code><b><i>Database.update()</i></b></code> Function</h2>
    <p>This function is use to update data of table.</p><br>
    <code>Database.update(table_name,column,value,from_where)</code>
    <div class="parameters">
        <h3>Parameters</h3>
        <p>It takes 4 parameters.</p>
        <ul>
            <li><code>table_name</code> The table in which you want to update data.</li>
            <li><code>column</code> Column name. <b>Must be a list.</b></li>
            <li><code>value</code> Value which going to be store in that. <b>Must be a list.</b></li>
            <li><code>from_where</code> Pair of column and value. <b>Must be a list.</b></li>
            <h4>Note</h4>
            <ul>
                <li><code>len(column)</code> == <code>len(value)</code></li>
                <li><code>column[0]</code> store the data in <code>value[0]</code></li>
            </ul>
        </ul>
    </div>
    <div class="return">
        <h3>Return</h3>
        <p>None</p>
    </div>
    <div class="examples">
        <h3>Examples</h3>
        <p>Here is an example.</p>
        <ul>
            <li><a href=""><b><i>Click here!</i></b></a></li>
        </ul>
    </div>
    
</div>

<div class="delete">
    <h2><code><b><i>Database.delete()</i></b></code> Function</h2>
    <p>This function is use to update data of table.</p><br>
    <code>Database.update(table_name,from_where)</code>
    <div class="parameters">
        <h3>Parameters</h3>
        <p>It takes 2 parameters.</p>
        <ul>
            <li><code>table_name</code> The table in which you want to delete data.</li>
            <li><code>from_where</code> Pair of column and value.</li>
        </ul>
    </div>
    <div class="return">
        <h3>Return</h3>
        <p>None</p>
    </div>
    <div class="examples">
        <h3>Examples</h3>
        <p>Here is an example.</p>
        <ul>
            <li><a href=""><b><i>Click here!</i></b></a></li>
        </ul>
    </div>

</div>
