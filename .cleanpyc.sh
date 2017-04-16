#!/bin/bash
echo 'Cleaning *.pyc'
rm $PWD/*.pyc 2&> /dev/null
echo 'Done!'
